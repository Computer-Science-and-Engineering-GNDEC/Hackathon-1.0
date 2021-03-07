# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, unittest
import frappe.defaults
from frappe.utils import flt, nowdate, nowtime
from erpnext.stock.doctype.serial_no.serial_no import *
from erpnext.stock.doctype.stock_ledger_entry.stock_ledger_entry import StockFreezeError
from erpnext.stock.stock_ledger import get_previous_sle
from frappe.permissions import add_user_permission, remove_user_permission
from erpnext.stock.doctype.stock_reconciliation.test_stock_reconciliation import create_stock_reconciliation
from erpnext.stock.doctype.item.test_item import set_item_variant_settings, make_item_variant, create_item
from erpnext.stock.doctype.stock_entry.stock_entry_utils import make_stock_entry
from erpnext.accounts.doctype.account.test_account import get_inventory_account
from erpnext.stock.doctype.stock_entry.stock_entry import move_sample_to_retention_warehouse, make_stock_in_entry
from erpnext.stock.doctype.stock_reconciliation.stock_reconciliation import OpeningEntryAccountError
from six import iteritems

def get_sle(**args):
	condition, values = "", []
	for key, value in iteritems(args):
		condition += " and " if condition else " where "
		condition += "`{0}`=%s".format(key)
		values.append(value)

	return frappe.db.sql("""select * from `tabStock Ledger Entry` %s
		order by timestamp(posting_date, posting_time) desc, creation desc limit 1"""% condition,
		values, as_dict=1)

class TestStockEntry(unittest.TestCase):
	def tearDown(self):
		frappe.set_user("Administrator")

	def test_fifo(self):
		frappe.db.set_value("Stock Settings", None, "allow_negative_stock", 1)
		item_code = "_Test Item 2"
		warehouse = "_Test Warehouse - _TC"

		create_stock_reconciliation(item_code="_Test Item 2", warehouse="_Test Warehouse - _TC",
			qty=0, rate=100)

		make_stock_entry(item_code=item_code, target=warehouse, qty=1, basic_rate=10)
		sle = get_sle(item_code = item_code, warehouse = warehouse)[0]

		self.assertEqual([[1, 10]], frappe.safe_eval(sle.stock_queue))

		# negative qty
		make_stock_entry(item_code=item_code, source=warehouse, qty=2, basic_rate=10)
		sle = get_sle(item_code = item_code, warehouse = warehouse)[0]

		self.assertEqual([[-1, 10]], frappe.safe_eval(sle.stock_queue))

		# further negative
		make_stock_entry(item_code=item_code, source=warehouse, qty=1)
		sle = get_sle(item_code = item_code, warehouse = warehouse)[0]

		self.assertEqual([[-2, 10]], frappe.safe_eval(sle.stock_queue))

		# move stock to positive
		make_stock_entry(item_code=item_code, target=warehouse, qty=3, basic_rate=20)
		sle = get_sle(item_code = item_code, warehouse = warehouse)[0]
		self.assertEqual([[1, 20]], frappe.safe_eval(sle.stock_queue))

		# incoming entry with diff rate
		make_stock_entry(item_code=item_code, target=warehouse, qty=1, basic_rate=30)
		sle = get_sle(item_code = item_code, warehouse = warehouse)[0]

		self.assertEqual([[1, 20],[1, 30]], frappe.safe_eval(sle.stock_queue))

		frappe.db.set_default("allow_negative_stock", 0)

	def test_auto_material_request(self):
		make_item_variant()
		self._test_auto_material_request("_Test Item")
		self._test_auto_material_request("_Test Item", material_request_type="Transfer")

	def test_auto_material_request_for_variant(self):
		fields = [{'field_name': 'reorder_levels'}]
		set_item_variant_settings(fields)
		make_item_variant()
		template = frappe.get_doc("Item", "_Test Variant Item")

		if not template.reorder_levels:
			template.append('reorder_levels', {
				"material_request_type": "Purchase",
				"warehouse": "_Test Warehouse - _TC",
				"warehouse_reorder_level": 20,
				"warehouse_reorder_qty": 20
			})

		template.save()
		self._test_auto_material_request("_Test Variant Item-S")

	def test_auto_material_request_for_warehouse_group(self):
		self._test_auto_material_request("_Test Item Warehouse Group Wise Reorder", warehouse="_Test Warehouse Group-C1 - _TC")

	def _test_auto_material_request(self, item_code, material_request_type="Purchase", warehouse="_Test Warehouse - _TC"):
		variant = frappe.get_doc("Item", item_code)

		projected_qty, actual_qty = frappe.db.get_value("Bin", {"item_code": item_code,
			"warehouse": warehouse}, ["projected_qty", "actual_qty"]) or [0, 0]

		# stock entry reqd for auto-reorder
		create_stock_reconciliation(item_code=item_code, warehouse=warehouse,
			qty = actual_qty + abs(projected_qty) + 10, rate=100)

		projected_qty = frappe.db.get_value("Bin", {"item_code": item_code,
			"warehouse": warehouse}, "projected_qty") or 0

		frappe.db.set_value("Stock Settings", None, "auto_indent", 1)

		# update re-level qty so that it is more than projected_qty
		if projected_qty >= variant.reorder_levels[0].warehouse_reorder_level:
			variant.reorder_levels[0].warehouse_reorder_level += projected_qty
			variant.reorder_levels[0].material_request_type = material_request_type
			variant.save()

		from erpnext.stock.reorder_item import reorder_item
		mr_list = reorder_item()

		frappe.db.set_value("Stock Settings", None, "auto_indent", 0)

		items = []
		for mr in mr_list:
			for d in mr.items:
				items.append(d.item_code)

		self.assertTrue(item_code in items)

	def test_material_receipt_gl_entry(self):
		company = frappe.db.get_value('Warehouse', 'Stores - TCP1', 'company')

		mr = make_stock_entry(item_code="_Test Item", target="Stores - TCP1", company= company,
			qty=50, basic_rate=100, expense_account="Stock Adjustment - TCP1")

		stock_in_hand_account = get_inventory_account(mr.company, mr.get("items")[0].t_warehouse)
		self.check_stock_ledger_entries("Stock Entry", mr.name,
			[["_Test Item", "Stores - TCP1", 50.0]])

		self.check_gl_entries("Stock Entry", mr.name,
			sorted([
				[stock_in_hand_account, 5000.0, 0.0],
				["Stock Adjustment - TCP1", 0.0, 5000.0]
			])
		)

		mr.cancel()

		self.assertTrue(frappe.db.sql("""select * from `tabStock Ledger Entry`
			where voucher_type='Stock Entry' and voucher_no=%s""", mr.name))

		self.assertTrue(frappe.db.sql("""select * from `tabGL Entry`
			where voucher_type='Stock Entry' and voucher_no=%s""", mr.name))

	def test_material_issue_gl_entry(self):
		company = frappe.db.get_value('Warehouse', 'Stores - TCP1', 'company')
		make_stock_entry(item_code="_Test Item", target="Stores - TCP1", company= company,
			qty=50, basic_rate=100, expense_account="Stock Adjustment - TCP1")

		mi = make_stock_entry(item_code="_Test Item", source="Stores - TCP1", company=company,
			qty=40, expense_account="Stock Adjustment - TCP1")

		self.check_stock_ledger_entries("Stock Entry", mi.name,
			[["_Test Item", "Stores - TCP1", -40.0]])

		stock_in_hand_account = get_inventory_account(mi.company, "Stores - TCP1")
		stock_value_diff = abs(frappe.db.get_value("Stock Ledger Entry", {"voucher_type": "Stock Entry",
			"voucher_no": mi.name}, "stock_value_difference"))

		self.check_gl_entries("Stock Entry", mi.name,
			sorted([
				[stock_in_hand_account, 0.0, stock_value_diff],
				["Stock Adjustment - TCP1", stock_value_diff, 0.0]
			])
		)
		mi.cancel()

	def test_material_transfer_gl_entry(self):
		company = frappe.db.get_value('Warehouse', 'Stores - TCP1', 'company')

		mtn = make_stock_entry(item_code="_Test Item", source="Stores - TCP1",
			target="Finished Goods - TCP1", qty=45, company=company)

		self.check_stock_ledger_entries("Stock Entry", mtn.name,
			[["_Test Item", "Stores - TCP1", -45.0], ["_Test Item", "Finished Goods - TCP1", 45.0]])

		source_warehouse_account = get_inventory_account(mtn.company, mtn.get("items")[0].s_warehouse)

		target_warehouse_account = get_inventory_account(mtn.company, mtn.get("items")[0].t_warehouse)

		if source_warehouse_account == target_warehouse_account:
			# no gl entry as both source and target warehouse has linked to same account.
			self.assertFalse(frappe.db.sql("""select * from `tabGL Entry`
				where voucher_type='Stock Entry' and voucher_no=%s""", mtn.name, as_dict=1))

		else:
			stock_value_diff = abs(frappe.db.get_value("Stock Ledger Entry", {"voucher_type": "Stock Entry",
				"voucher_no": mtn.name, "warehouse": "Stores - TCP1"}, "stock_value_difference"))

			self.check_gl_entries("Stock Entry", mtn.name,
				sorted([
					[source_warehouse_account, 0.0, stock_value_diff],
					[target_warehouse_account, stock_value_diff, 0.0],
				])
			)

		mtn.cancel()

	def test_repack_no_change_in_valuation(self):
		company = frappe.db.get_value('Warehouse', '_Test Warehouse - _TC', 'company')

		make_stock_entry(item_code="_Test Item", target="_Test Warehouse - _TC", qty=50, basic_rate=100)
		make_stock_entry(item_code="_Test Item Home Desktop 100", target="_Test Warehouse - _TC",
			qty=50, basic_rate=100)

		repack = frappe.copy_doc(test_records[3])
		repack.posting_date = nowdate()
		repack.posting_time = nowtime()
		repack.set_stock_entry_type()
		repack.insert()
		repack.submit()

		self.check_stock_ledger_entries("Stock Entry", repack.name,
			[["_Test Item", "_Test Warehouse - _TC", -50.0],
				["_Test Item Home Desktop 100", "_Test Warehouse - _TC", 1]])

		gl_entries = frappe.db.sql("""select account, debit, credit
			from `tabGL Entry` where voucher_type='Stock Entry' and voucher_no=%s
			order by account desc""", repack.name, as_dict=1)
		self.assertFalse(gl_entries)

	def test_repack_with_additional_costs(self):
		company = frappe.db.get_value('Warehouse', 'Stores - TCP1', 'company')

		make_stock_entry(item_code="_Test Item", target="Stores - TCP1", company= company,
			qty=50, basic_rate=100, expense_account="Stock Adjustment - TCP1")


		repack = make_stock_entry(company = company, purpose="Repack", do_not_save=True)
		repack.posting_date = nowdate()
		repack.posting_time = nowtime()

		expenses_included_in_valuation = frappe.get_value("Company", company, "expenses_included_in_valuation")

		items = get_multiple_items()
		repack.items = []
		for item in items:
			repack.append("items", item)

		repack.set("additional_costs", [
			{
				"expense_account": expenses_included_in_valuation,
				"description": "Actual Operating Cost",
				"amount": 1000
			},
			{
				"expense_account": expenses_included_in_valuation,
				"description": "Additional Operating Cost",
				"amount": 200
			},
		])

		repack.set_stock_entry_type()
		repack.insert()
		repack.submit()

		stock_in_hand_account = get_inventory_account(repack.company, repack.get("items")[1].t_warehouse)
		rm_stock_value_diff = abs(frappe.db.get_value("Stock Ledger Entry", {"voucher_type": "Stock Entry",
			"voucher_no": repack.name, "item_code": "_Test Item"}, "stock_value_difference"))

		fg_stock_value_diff = abs(frappe.db.get_value("Stock Ledger Entry", {"voucher_type": "Stock Entry",
			"voucher_no": repack.name, "item_code": "_Test Item Home Desktop 100"}, "stock_value_difference"))

		stock_value_diff = flt(fg_stock_value_diff - rm_stock_value_diff, 2)

		self.assertEqual(stock_value_diff, 1200)

		self.check_gl_entries("Stock Entry", repack.name,
			sorted([
				[stock_in_hand_account, 1200, 0.0],
				["Expenses Included In Valuation - TCP1", 0.0, 1200.0]
			])
		)

	def check_stock_ledger_entries(self, voucher_type, voucher_no, expected_sle):
		expected_sle.sort(key=lambda x: x[1])

		# check stock ledger entries
		sle = frappe.db.sql("""select item_code, warehouse, actual_qty
			from `tabStock Ledger Entry` where voucher_type = %s
			and voucher_no = %s order by item_code, warehouse, actual_qty""",
			(voucher_type, voucher_no), as_list=1)
		self.assertTrue(sle)
		sle.sort(key=lambda x: x[1])

		for i, sle in enumerate(sle):
			self.assertEqual(expected_sle[i][0], sle[0])
			self.assertEqual(expected_sle[i][1], sle[1])
			self.assertEqual(expected_sle[i][2], sle[2])

	def check_gl_entries(self, voucher_type, voucher_no, expected_gl_entries):
		expected_gl_entries.sort(key=lambda x: x[0])

		gl_entries = frappe.db.sql("""select account, debit, credit
			from `tabGL Entry` where voucher_type=%s and voucher_no=%s
			order by account asc, debit asc""", (voucher_type, voucher_no), as_list=1)

		self.assertTrue(gl_entries)
		gl_entries.sort(key=lambda x: x[0])
		for i, gle in enumerate(gl_entries):
			self.assertEqual(expected_gl_entries[i][0], gle[0])
			self.assertEqual(expected_gl_entries[i][1], gle[1])
			self.assertEqual(expected_gl_entries[i][2], gle[2])

	def test_serial_no_not_reqd(self):
		se = frappe.copy_doc(test_records[0])
		se.get("items")[0].serial_no = "ABCD"
		se.set_stock_entry_type()
		se.insert()
		self.assertRaises(SerialNoNotRequiredError, se.submit)

	def test_serial_no_reqd(self):
		se = frappe.copy_doc(test_records[0])
		se.get("items")[0].item_code = "_Test Serialized Item"
		se.get("items")[0].qty = 2
		se.get("items")[0].transfer_qty = 2
		se.set_stock_entry_type()
		se.insert()
		self.assertRaises(SerialNoRequiredError, se.submit)

	def test_serial_no_qty_more(self):
		se = frappe.copy_doc(test_records[0])
		se.get("items")[0].item_code = "_Test Serialized Item"
		se.get("items")[0].qty = 2
		se.get("items")[0].serial_no = "ABCD\nEFGH\nXYZ"
		se.get("items")[0].transfer_qty = 2
		se.set_stock_entry_type()
		se.insert()
		self.assertRaises(SerialNoQtyError, se.submit)

	def test_serial_no_qty_less(self):
		se = frappe.copy_doc(test_records[0])
		se.get("items")[0].item_code = "_Test Serialized Item"
		se.get("items")[0].qty = 2
		se.get("items")[0].serial_no = "ABCD"
		se.get("items")[0].transfer_qty = 2
		se.set_stock_entry_type()
		se.insert()
		self.assertRaises(SerialNoQtyError, se.submit)

	def test_serial_no_transfer_in(self):
		se = frappe.copy_doc(test_records[0])
		se.get("items")[0].item_code = "_Test Serialized Item"
		se.get("items")[0].qty = 2
		se.get("items")[0].serial_no = "ABCD\nEFGH"
		se.get("items")[0].transfer_qty = 2
		se.set_stock_entry_type()
		se.insert()
		se.submit()

		self.assertTrue(frappe.db.exists("Serial No", "ABCD"))
		self.assertTrue(frappe.db.exists("Serial No", "EFGH"))

		se.cancel()
		self.assertFalse(frappe.db.get_value("Serial No", "ABCD", "warehouse"))

	def test_serial_no_not_exists(self):
		frappe.db.sql("delete from `tabSerial No` where name in ('ABCD', 'EFGH')")
		make_serialized_item(target_warehouse="_Test Warehouse 1 - _TC")
		se = frappe.copy_doc(test_records[0])
		se.purpose = "Material Issue"
		se.get("items")[0].item_code = "_Test Serialized Item With Series"
		se.get("items")[0].qty = 2
		se.get("items")[0].s_warehouse = "_Test Warehouse 1 - _TC"
		se.get("items")[0].t_warehouse = None
		se.get("items")[0].serial_no = "ABCD\nEFGH"
		se.get("items")[0].transfer_qty = 2
		se.set_stock_entry_type()
		se.insert()

		self.assertRaises(SerialNoNotExistsError, se.submit)

	def test_serial_duplicate(self):
		se, serial_nos = self.test_serial_by_series()

		se = frappe.copy_doc(test_records[0])
		se.get("items")[0].item_code = "_Test Serialized Item With Series"
		se.get("items")[0].qty = 1
		se.get("items")[0].serial_no = serial_nos[0]
		se.get("items")[0].transfer_qty = 1
		se.set_stock_entry_type()
		se.insert()
		self.assertRaises(SerialNoDuplicateError, se.submit)

	def test_serial_by_series(self):
		se = make_serialized_item()

		serial_nos = get_serial_nos(se.get("items")[0].serial_no)

		self.assertTrue(frappe.db.exists("Serial No", serial_nos[0]))
		self.assertTrue(frappe.db.exists("Serial No", serial_nos[1]))

		return se, serial_nos

	def test_serial_item_error(self):
		se, serial_nos = self.test_serial_by_series()
		if not frappe.db.exists('Serial No', 'ABCD'):
			make_serialized_item(item_code="_Test Serialized Item", serial_no="ABCD\nEFGH")

		se = frappe.copy_doc(test_records[0])
		se.purpose = "Material Transfer"
		se.get("items")[0].item_code = "_Test Serialized Item"
		se.get("items")[0].qty = 1
		se.get("items")[0].transfer_qty = 1
		se.get("items")[0].serial_no = serial_nos[0]
		se.get("items")[0].s_warehouse = "_Test Warehouse - _TC"
		se.get("items")[0].t_warehouse = "_Test Warehouse 1 - _TC"
		se.set_stock_entry_type()
		se.insert()
		self.assertRaises(SerialNoItemError, se.submit)

	def test_serial_move(self):
		se = make_serialized_item()
		serial_no = get_serial_nos(se.get("items")[0].serial_no)[0]

		se = frappe.copy_doc(test_records[0])
		se.purpose = "Material Transfer"
		se.get("items")[0].item_code = "_Test Serialized Item With Series"
		se.get("items")[0].qty = 1
		se.get("items")[0].transfer_qty = 1
		se.get("items")[0].serial_no = serial_no
		se.get("items")[0].s_warehouse = "_Test Warehouse - _TC"
		se.get("items")[0].t_warehouse = "_Test Warehouse 1 - _TC"
		se.set_stock_entry_type()
		se.insert()
		se.submit()
		self.assertTrue(frappe.db.get_value("Serial No", serial_no, "warehouse"), "_Test Warehouse 1 - _TC")

		se.cancel()
		self.assertTrue(frappe.db.get_value("Serial No", serial_no, "warehouse"), "_Test Warehouse - _TC")

	def test_serial_warehouse_error(self):
		make_serialized_item(target_warehouse="_Test Warehouse 1 - _TC")

		t = make_serialized_item()
		serial_nos = get_serial_nos(t.get("items")[0].serial_no)

		se = frappe.copy_doc(test_records[0])
		se.purpose = "Material Transfer"
		se.get("items")[0].item_code = "_Test Serialized Item With Series"
		se.get("items")[0].qty = 1
		se.get("items")[0].transfer_qty = 1
		se.get("items")[0].serial_no = serial_nos[0]
		se.get("items")[0].s_warehouse = "_Test Warehouse 1 - _TC"
		se.get("items")[0].t_warehouse = "_Test Warehouse - _TC"
		se.set_stock_entry_type()
		se.insert()
		self.assertRaises(SerialNoWarehouseError, se.submit)

	def test_serial_cancel(self):
		se, serial_nos = self.test_serial_by_series()
		se.cancel()

		serial_no = get_serial_nos(se.get("items")[0].serial_no)[0]
		self.assertFalse(frappe.db.get_value("Serial No", serial_no, "warehouse"))

	def test_warehouse_company_validation(self):
		company = frappe.db.get_value('Warehouse', '_Test Warehouse 2 - _TC1', 'company')
		frappe.get_doc("User", "test2@example.com")\
			.add_roles("Sales User", "Sales Manager", "Stock User", "Stock Manager")
		frappe.set_user("test2@example.com")

		from erpnext.stock.utils import InvalidWarehouseCompany
		st1 = frappe.copy_doc(test_records[0])
		st1.get("items")[0].t_warehouse="_Test Warehouse 2 - _TC1"
		st1.set_stock_entry_type()
		st1.insert()
		self.assertRaises(InvalidWarehouseCompany, st1.submit)

	# permission tests
	def test_warehouse_user(self):
		add_user_permission("Warehouse", "_Test Warehouse 1 - _TC", "test@example.com")
		add_user_permission("Warehouse", "_Test Warehouse 2 - _TC1", "test2@example.com")
		add_user_permission("Company", "_Test Company 1", "test2@example.com")
		test_user = frappe.get_doc("User", "test@example.com")
		test_user.add_roles("Sales User", "Sales Manager", "Stock User")
		test_user.remove_roles("Stock Manager", "System Manager")

		frappe.get_doc("User", "test2@example.com")\
			.add_roles("Sales User", "Sales Manager", "Stock User", "Stock Manager")

		st1 = frappe.copy_doc(test_records[0])
		st1.company = "_Test Company 1"

		frappe.set_user("test@example.com")
		st1.get("items")[0].t_warehouse="_Test Warehouse 2 - _TC1"
		self.assertRaises(frappe.PermissionError, st1.insert)

		test_user.add_roles("System Manager")

		frappe.set_user("test2@example.com")
		st1 = frappe.copy_doc(test_records[0])
		st1.company = "_Test Company 1"
		st1.get("items")[0].t_warehouse="_Test Warehouse 2 - _TC1"
		st1.get("items")[0].expense_account = "Stock Adjustment - _TC1"
		st1.get("items")[0].cost_center = "Main - _TC1"
		st1.set_stock_entry_type()
		st1.insert()
		st1.submit()

		frappe.set_user("Administrator")
		remove_user_permission("Warehouse", "_Test Warehouse 1 - _TC", "test@example.com")
		remove_user_permission("Warehouse", "_Test Warehouse 2 - _TC1", "test2@example.com")
		remove_user_permission("Company", "_Test Company 1", "test2@example.com")

	def test_freeze_stocks(self):
		frappe.db.set_value('Stock Settings', None,'stock_auth_role', '')

		# test freeze_stocks_upto
		frappe.db.set_value("Stock Settings", None, "stock_frozen_upto", add_days(nowdate(), 5))
		se = frappe.copy_doc(test_records[0]).insert()
		self.assertRaises(StockFreezeError, se.submit)

		frappe.db.set_value("Stock Settings", None, "stock_frozen_upto", '')

		# test freeze_stocks_upto_days
		frappe.db.set_value("Stock Settings", None, "stock_frozen_upto_days", -1)
		se = frappe.copy_doc(test_records[0])
		se.set_posting_time = 1
		se.posting_date = nowdate()
		se.set_stock_entry_type()
		se.insert()
		self.assertRaises(StockFreezeError, se.submit)
		frappe.db.set_value("Stock Settings", None, "stock_frozen_upto_days", 0)

	def test_work_order(self):
		from erpnext.manufacturing.doctype.work_order.work_order \
			import make_stock_entry as _make_stock_entry
		bom_no, bom_operation_cost = frappe.db.get_value("BOM", {"item": "_Test FG Item 2",
			"is_default": 1, "docstatus": 1}, ["name", "operating_cost"])

		work_order = frappe.new_doc("Work Order")
		work_order.update({
			"company": "_Test Company",
			"fg_warehouse": "_Test Warehouse 1 - _TC",
			"production_item": "_Test FG Item 2",
			"bom_no": bom_no,
			"qty": 1.0,
			"stock_uom": "_Test UOM",
			"wip_warehouse": "_Test Warehouse - _TC",
			"additional_operating_cost": 1000
		})
		work_order.insert()
		work_order.submit()

		make_stock_entry(item_code="_Test Item", target="_Test Warehouse - _TC", qty=50, basic_rate=100)
		make_stock_entry(item_code="_Test Item 2", target="_Test Warehouse - _TC", qty=50, basic_rate=20)

		stock_entry = _make_stock_entry(work_order.name, "Manufacture", 1)

		rm_cost = 0
		for d in stock_entry.get("items"):
			if d.item_code != "_Test FG Item 2":
				rm_cost += flt(d.amount)
		fg_cost = list(filter(lambda x: x.item_code=="_Test FG Item 2", stock_entry.get("items")))[0].amount
		self.assertEqual(fg_cost,
			flt(rm_cost + bom_operation_cost + work_order.additional_operating_cost, 2))


	def test_variant_work_order(self):
		bom_no = frappe.db.get_value("BOM", {"item": "_Test Variant Item",
			"is_default": 1, "docstatus": 1})

		work_order = frappe.new_doc("Work Order")
		work_order.update({
			"company": "_Test Company",
			"fg_warehouse": "_Test Warehouse 1 - _TC",
			"production_item": "_Test Variant Item-S",
			"bom_no": bom_no,
			"qty": 1.0,
			"stock_uom": "_Test UOM",
			"wip_warehouse": "_Test Warehouse - _TC",
			"skip_transfer": 1
		})
		work_order.insert()
		work_order.submit()

		from erpnext.manufacturing.doctype.work_order.work_order import make_stock_entry

		stock_entry = frappe.get_doc(make_stock_entry(work_order.name, "Manufacture", 1))
		stock_entry.insert()
		self.assertTrue("_Test Variant Item-S" in [d.item_code for d in stock_entry.items])

	def test_same_serial_nos_in_repack_or_manufacture_entries(self):
		s1 = make_serialized_item(target_warehouse="_Test Warehouse - _TC")
		serial_nos = s1.get("items")[0].serial_no

		s2 = make_stock_entry(item_code="_Test Serialized Item With Series", source="_Test Warehouse - _TC",
			qty=2, basic_rate=100, purpose="Repack", serial_no=serial_nos, do_not_save=True)

		s2.append("items", {
			"item_code": "_Test Serialized Item",
			"t_warehouse": "_Test Warehouse - _TC",
			"qty": 2,
			"basic_rate": 120,
			"expense_account": "Stock Adjustment - _TC",
			"conversion_factor": 1.0,
			"cost_center": "_Test Cost Center - _TC",
			"serial_no": serial_nos
		})

		s2.submit()
		s2.cancel()

	def test_retain_sample(self):
		from erpnext.stock.doctype.warehouse.test_warehouse import create_warehouse
		from erpnext.stock.doctype.batch.batch import get_batch_qty

		create_warehouse("Test Warehouse for Sample Retention")
		frappe.db.set_value("Stock Settings", None, "sample_retention_warehouse", "Test Warehouse for Sample Retention - _TC")

		test_item_code = "Retain Sample Item"
		if not frappe.db.exists('Item', test_item_code):
			item = frappe.new_doc("Item")
			item.item_code = test_item_code
			item.item_name = "Retain Sample Item"
			item.description = "Retain Sample Item"
			item.item_group = "All Item Groups"
			item.is_stock_item = 1
			item.has_batch_no = 1
			item.create_new_batch = 1
			item.retain_sample = 1
			item.sample_quantity = 4
			item.save()

		receipt_entry = frappe.new_doc("Stock Entry")
		receipt_entry.company = "_Test Company"
		receipt_entry.purpose = "Material Receipt"
		receipt_entry.append("items", {
			"item_code": test_item_code,
			"t_warehouse": "_Test Warehouse - _TC",
			"qty": 40,
			"basic_rate": 12,
			"cost_center": "_Test Cost Center - _TC",
			"sample_quantity": 4
		})
		receipt_entry.set_stock_entry_type()
		receipt_entry.insert()
		receipt_entry.submit()

		retention_data = move_sample_to_retention_warehouse(receipt_entry.company, receipt_entry.get("items"))
		retention_entry = frappe.new_doc("Stock Entry")
		retention_entry.company = retention_data.company
		retention_entry.purpose = retention_data.purpose
		retention_entry.append("items", {
			"item_code": test_item_code,
			"t_warehouse": "Test Warehouse for Sample Retention - _TC",
			"s_warehouse": "_Test Warehouse - _TC",
			"qty": 4,
			"basic_rate": 12,
			"cost_center": "_Test Cost Center - _TC",
			"batch_no": receipt_entry.get("items")[0].batch_no
		})
		retention_entry.set_stock_entry_type()
		retention_entry.insert()
		retention_entry.submit()

		qty_in_usable_warehouse = get_batch_qty(receipt_entry.get("items")[0].batch_no, "_Test Warehouse - _TC", "_Test Item")
		qty_in_retention_warehouse = get_batch_qty(receipt_entry.get("items")[0].batch_no, "Test Warehouse for Sample Retention - _TC", "_Test Item")

		self.assertEqual(qty_in_usable_warehouse, 36)
		self.assertEqual(qty_in_retention_warehouse, 4)

	def test_quality_check(self):
		item_code = "_Test Item For QC"
		if not frappe.db.exists('Item', item_code):
			create_item(item_code)

		repack = frappe.copy_doc(test_records[3])
		repack.inspection_required = 1
		for d in repack.items:
			if not d.s_warehouse and d.t_warehouse:
				d.item_code = item_code
				d.qty = 1
				d.uom = "Nos"
				d.stock_uom = "Nos"
				d.basic_rate = 5000

		repack.insert()
		self.assertRaises(frappe.ValidationError, repack.submit)

	# def test_material_consumption(self):
	# 	frappe.db.set_value("Manufacturing Settings", None, "backflush_raw_materials_based_on", "BOM")
	# 	frappe.db.set_value("Manufacturing Settings", None, "material_consumption", "0")

	# 	from erpnext.manufacturing.doctype.work_order.work_order \
	# 		import make_stock_entry as _make_stock_entry
	# 	bom_no = frappe.db.get_value("BOM", {"item": "_Test FG Item 2",
	# 		"is_default": 1, "docstatus": 1})

	# 	work_order = frappe.new_doc("Work Order")
	# 	work_order.update({
	# 		"company": "_Test Company",
	# 		"fg_warehouse": "_Test Warehouse 1 - _TC",
	# 		"production_item": "_Test FG Item 2",
	# 		"bom_no": bom_no,
	# 		"qty": 4.0,
	# 		"stock_uom": "_Test UOM",
	# 		"wip_warehouse": "_Test Warehouse - _TC",
	# 		"additional_operating_cost": 1000,
	# 		"use_multi_level_bom": 1
	# 	})
	# 	work_order.insert()
	# 	work_order.submit()

	# 	make_stock_entry(item_code="_Test Serialized Item With Series", target="_Test Warehouse - _TC", qty=50, basic_rate=100)
	# 	make_stock_entry(item_code="_Test Item 2", target="_Test Warehouse - _TC", qty=50, basic_rate=20)

	# 	item_quantity = {
	# 		'_Test Item': 2.0,
	# 		'_Test Item 2': 12.0,
	# 		'_Test Serialized Item With Series': 6.0
	# 	}

	# 	stock_entry = frappe.get_doc(_make_stock_entry(work_order.name, "Material Consumption for Manufacture", 2))
	# 	for d in stock_entry.get('items'):
	# 		self.assertEqual(item_quantity.get(d.item_code), d.qty)

	def test_customer_provided_parts_se(self):
		create_item('CUST-0987', is_customer_provided_item = 1, customer = '_Test Customer', is_purchase_item = 0)
		se = make_stock_entry(item_code='CUST-0987', purpose = 'Material Receipt',
			qty=4, to_warehouse = "_Test Warehouse - _TC")
		self.assertEqual(se.get("items")[0].allow_zero_valuation_rate, 1)
		self.assertEqual(se.get("items")[0].amount, 0)

	def test_gle_for_opening_stock_entry(self):
		mr = make_stock_entry(item_code="_Test Item", target="Stores - TCP1",
			company="_Test Company with perpetual inventory", qty=50, basic_rate=100,
			expense_account="Stock Adjustment - TCP1", is_opening="Yes", do_not_save=True)

		self.assertRaises(OpeningEntryAccountError, mr.save)

		mr.items[0].expense_account = "Temporary Opening - TCP1"

		mr.save()
		mr.submit()

		is_opening = frappe.db.get_value("GL Entry",
			filters={"voucher_type": "Stock Entry", "voucher_no": mr.name}, fieldname="is_opening")
		self.assertEqual(is_opening, "Yes")

	def test_total_basic_amount_zero(self):
		se = frappe.get_doc({"doctype":"Stock Entry",
			"purpose":"Material Receipt",
			"stock_entry_type":"Material Receipt",
			"posting_date": nowdate(),
			"company":"_Test Company with perpetual inventory",
			"items":[
				{
					"item_code":"_Test Item",
					"description":"_Test Item",
					"qty": 1,
					"basic_rate": 0,
					"uom":"Nos",
					"t_warehouse": "Stores - TCP1",
					"allow_zero_valuation_rate": 1,
					"cost_center": "Main - TCP1"
				},
				{
					"item_code":"_Test Item",
					"description":"_Test Item",
					"qty": 2,
					"basic_rate": 0,
					"uom":"Nos",
					"t_warehouse": "Stores - TCP1",
					"allow_zero_valuation_rate": 1,
					"cost_center": "Main - TCP1"
				},
			],
			"additional_costs":[
				{"expense_account":"Miscellaneous Expenses - TCP1",
				"amount":100,
				"description": "miscellanous"
			}]
		})
		se.insert()
		se.submit()

		self.check_gl_entries("Stock Entry", se.name,
			sorted([
				["Stock Adjustment - TCP1", 100.0, 0.0],
				["Miscellaneous Expenses - TCP1", 0.0, 100.0]
			])
		)

	def test_conversion_factor_change(self):
		frappe.db.set_value("Stock Settings", None, "allow_negative_stock", 1)
		repack_entry = frappe.copy_doc(test_records[3])
		repack_entry.posting_date = nowdate()
		repack_entry.posting_time = nowtime()
		repack_entry.set_stock_entry_type()
		repack_entry.insert()

		# check current uom and conversion factor
		self.assertTrue(repack_entry.items[0].uom, "_Test UOM")
		self.assertTrue(repack_entry.items[0].conversion_factor, 1)

		# change conversion factor
		repack_entry.items[0].uom = "_Test UOM 1"
		repack_entry.items[0].stock_uom = "_Test UOM 1"
		repack_entry.items[0].conversion_factor = 2
		repack_entry.save()
		repack_entry.submit()

		self.assertEqual(repack_entry.items[0].conversion_factor, 2)
		self.assertEqual(repack_entry.items[0].uom, "_Test UOM 1")
		self.assertEqual(repack_entry.items[0].qty, 50)
		self.assertEqual(repack_entry.items[0].transfer_qty, 100)

		frappe.db.set_default("allow_negative_stock", 0)

def make_serialized_item(**args):
	args = frappe._dict(args)
	se = frappe.copy_doc(test_records[0])

	if args.company:
		se.company = args.company

	se.get("items")[0].item_code = args.item_code or "_Test Serialized Item With Series"

	if args.serial_no:
		se.get("items")[0].serial_no = args.serial_no

	if args.cost_center:
		se.get("items")[0].cost_center = args.cost_center

	if args.expense_account:
		se.get("items")[0].expense_account = args.expense_account

	se.get("items")[0].qty = 2
	se.get("items")[0].transfer_qty = 2

	if args.target_warehouse:
		se.get("items")[0].t_warehouse = args.target_warehouse

	se.set_stock_entry_type()
	se.insert()
	se.submit()
	return se

def get_qty_after_transaction(**args):
	args = frappe._dict(args)
	last_sle = get_previous_sle({
		"item_code": args.item_code or "_Test Item",
		"warehouse": args.warehouse or "_Test Warehouse - _TC",
		"posting_date": args.posting_date or nowdate(),
		"posting_time": args.posting_time or nowtime()
	})
	return flt(last_sle.get("qty_after_transaction"))

def get_multiple_items():
	return [
			{
				"conversion_factor": 1.0,
				"cost_center": "Main - TCP1",
				"doctype": "Stock Entry Detail",
				"expense_account": "Stock Adjustment - TCP1",
				"basic_rate": 100,
				"item_code": "_Test Item",
				"qty": 50.0,
				"s_warehouse": "Stores - TCP1",
				"stock_uom": "_Test UOM",
				"transfer_qty": 50.0,
				"uom": "_Test UOM"
			},
			{
				"conversion_factor": 1.0,
				"cost_center": "Main - TCP1",
				"doctype": "Stock Entry Detail",
				"expense_account": "Stock Adjustment - TCP1",
				"basic_rate": 5000,
				"item_code": "_Test Item Home Desktop 100",
				"qty": 1,
				"stock_uom": "_Test UOM",
				"t_warehouse": "Stores - TCP1",
				"transfer_qty": 1,
				"uom": "_Test UOM"
			}
		]

test_records = frappe.get_test_records('Stock Entry')
