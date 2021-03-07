# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest, copy, time
from erpnext.accounts.doctype.pos_profile.test_pos_profile import make_pos_profile
from erpnext.accounts.doctype.pos_invoice.pos_invoice import make_sales_return
from erpnext.stock.doctype.stock_entry.stock_entry_utils import make_stock_entry
from erpnext.stock.doctype.purchase_receipt.test_purchase_receipt import make_purchase_receipt

class TestPOSInvoice(unittest.TestCase):
	def test_timestamp_change(self):
		w = create_pos_invoice(do_not_save=1)
		w.docstatus = 0
		w.insert()

		w2 = frappe.get_doc(w.doctype, w.name)

		import time
		time.sleep(1)
		w.save()

		import time
		time.sleep(1)
		self.assertRaises(frappe.TimestampMismatchError, w2.save)

	def test_change_naming_series(self):
		inv = create_pos_invoice(do_not_submit=1)
		inv.naming_series = 'TEST-'

		self.assertRaises(frappe.CannotChangeConstantError, inv.save)

	def test_discount_and_inclusive_tax(self):
		inv = create_pos_invoice(qty=100, rate=50, do_not_save=1)
		inv.append("taxes", {
			"charge_type": "On Net Total",
			"account_head": "_Test Account Service Tax - _TC",
			"cost_center": "_Test Cost Center - _TC",
			"description": "Service Tax",
			"rate": 14,
			'included_in_print_rate': 1
		})
		inv.insert()

		self.assertEqual(inv.net_total, 4385.96)
		self.assertEqual(inv.grand_total, 5000)

		inv.reload()

		inv.discount_amount = 100
		inv.apply_discount_on = 'Net Total'
		inv.payment_schedule = []

		inv.save()

		self.assertEqual(inv.net_total, 4285.96)
		self.assertEqual(inv.grand_total, 4885.99)

		inv.reload()

		inv.discount_amount = 100
		inv.apply_discount_on = 'Grand Total'
		inv.payment_schedule = []

		inv.save()

		self.assertEqual(inv.net_total, 4298.25)
		self.assertEqual(inv.grand_total, 4900.00)

	def test_tax_calculation_with_multiple_items(self):
		inv = create_pos_invoice(qty=84, rate=4.6, do_not_save=True)
		item_row = inv.get("items")[0]
		for qty in (54, 288, 144, 430):
			item_row_copy = copy.deepcopy(item_row)
			item_row_copy.qty = qty
			inv.append("items", item_row_copy)

		inv.append("taxes", {
			"account_head": "_Test Account VAT - _TC",
			"charge_type": "On Net Total",
			"cost_center": "_Test Cost Center - _TC",
			"description": "VAT",
			"doctype": "Sales Taxes and Charges",
			"rate": 19
		})
		inv.insert()

		self.assertEqual(inv.net_total, 4600)

		self.assertEqual(inv.get("taxes")[0].tax_amount, 874.0)
		self.assertEqual(inv.get("taxes")[0].total, 5474.0)

		self.assertEqual(inv.grand_total, 5474.0)

	def test_tax_calculation_with_item_tax_template(self):
		inv = create_pos_invoice(qty=84, rate=4.6, do_not_save=1)
		item_row = inv.get("items")[0]

		add_items = [
			(54, '_Test Account Excise Duty @ 12'),
			(288, '_Test Account Excise Duty @ 15'),
			(144, '_Test Account Excise Duty @ 20'),
			(430, '_Test Item Tax Template 1')
		]
		for qty, item_tax_template in add_items:
			item_row_copy = copy.deepcopy(item_row)
			item_row_copy.qty = qty
			item_row_copy.item_tax_template = item_tax_template
			inv.append("items", item_row_copy)

		inv.append("taxes", {
			"account_head": "_Test Account Excise Duty - _TC",
			"charge_type": "On Net Total",
			"cost_center": "_Test Cost Center - _TC",
			"description": "Excise Duty",
			"doctype": "Sales Taxes and Charges",
			"rate": 11
		})
		inv.append("taxes", {
			"account_head": "_Test Account Education Cess - _TC",
			"charge_type": "On Net Total",
			"cost_center": "_Test Cost Center - _TC",
			"description": "Education Cess",
			"doctype": "Sales Taxes and Charges",
			"rate": 0
		})
		inv.append("taxes", {
			"account_head": "_Test Account S&H Education Cess - _TC",
			"charge_type": "On Net Total",
			"cost_center": "_Test Cost Center - _TC",
			"description": "S&H Education Cess",
			"doctype": "Sales Taxes and Charges",
			"rate": 3
		})
		inv.insert()

		self.assertEqual(inv.net_total, 4600)

		self.assertEqual(inv.get("taxes")[0].tax_amount, 502.41)
		self.assertEqual(inv.get("taxes")[0].total, 5102.41)

		self.assertEqual(inv.get("taxes")[1].tax_amount, 197.80)
		self.assertEqual(inv.get("taxes")[1].total, 5300.21)

		self.assertEqual(inv.get("taxes")[2].tax_amount, 375.36)
		self.assertEqual(inv.get("taxes")[2].total, 5675.57)

		self.assertEqual(inv.grand_total, 5675.57)
		self.assertEqual(inv.rounding_adjustment, 0.43)
		self.assertEqual(inv.rounded_total, 5676.0)

	def test_tax_calculation_with_multiple_items_and_discount(self):
		inv = create_pos_invoice(qty=1, rate=75, do_not_save=True)
		item_row = inv.get("items")[0]
		for rate in (500, 200, 100, 50, 50):
			item_row_copy = copy.deepcopy(item_row)
			item_row_copy.price_list_rate = rate
			item_row_copy.rate = rate
			inv.append("items", item_row_copy)

		inv.apply_discount_on = "Net Total"
		inv.discount_amount = 75.0

		inv.append("taxes", {
			"account_head": "_Test Account VAT - _TC",
			"charge_type": "On Net Total",
			"cost_center": "_Test Cost Center - _TC",
			"description": "VAT",
			"doctype": "Sales Taxes and Charges",
			"rate": 24
		})
		inv.insert()

		self.assertEqual(inv.total, 975)
		self.assertEqual(inv.net_total, 900)

		self.assertEqual(inv.get("taxes")[0].tax_amount, 216.0)
		self.assertEqual(inv.get("taxes")[0].total, 1116.0)

		self.assertEqual(inv.grand_total, 1116.0)

	def test_pos_returns_with_repayment(self):
		pos = create_pos_invoice(qty = 10, do_not_save=True)

		pos.set('payments', [])
		pos.append("payments", {'mode_of_payment': 'Bank Draft', 'account': '_Test Bank - _TC', 'amount': 500})
		pos.append("payments", {'mode_of_payment': 'Cash', 'account': 'Cash - _TC', 'amount': 500, 'default': 1})
		pos.insert()
		pos.submit()

		pos_return = make_sales_return(pos.name)

		pos_return.insert()
		pos_return.submit()

		self.assertEqual(pos_return.get('payments')[0].amount, -500)
		self.assertEqual(pos_return.get('payments')[1].amount, -500)

	def test_pos_return_for_serialized_item(self):
		from erpnext.stock.doctype.stock_entry.test_stock_entry import make_serialized_item
		from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos

		se = make_serialized_item(company='_Test Company',
			target_warehouse="Stores - _TC", cost_center='Main - _TC', expense_account='Cost of Goods Sold - _TC')

		serial_nos = get_serial_nos(se.get("items")[0].serial_no)

		pos = create_pos_invoice(company='_Test Company', debit_to='Debtors - _TC',
			account_for_change_amount='Cash - _TC', warehouse='Stores - _TC', income_account='Sales - _TC',
			expense_account='Cost of Goods Sold - _TC', cost_center='Main - _TC',
			item=se.get("items")[0].item_code, rate=1000, do_not_save=1)

		pos.get("items")[0].serial_no = serial_nos[0]
		pos.append("payments", {'mode_of_payment': 'Cash', 'account': 'Cash - _TC', 'amount': 1000, 'default': 1})

		pos.insert()
		pos.submit()

		pos_return = make_sales_return(pos.name)

		pos_return.insert()
		pos_return.submit()
		self.assertEqual(pos_return.get('items')[0].serial_no, serial_nos[0])

	def test_partial_pos_returns(self):
		from erpnext.stock.doctype.stock_entry.test_stock_entry import make_serialized_item
		from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos

		se = make_serialized_item(company='_Test Company',
			target_warehouse="Stores - _TC", cost_center='Main - _TC', expense_account='Cost of Goods Sold - _TC')

		serial_nos = get_serial_nos(se.get("items")[0].serial_no)

		pos = create_pos_invoice(company='_Test Company', debit_to='Debtors - _TC',
			account_for_change_amount='Cash - _TC', warehouse='Stores - _TC', income_account='Sales - _TC',
			expense_account='Cost of Goods Sold - _TC', cost_center='Main - _TC',
			item=se.get("items")[0].item_code, qty=2, rate=1000, do_not_save=1)

		pos.get("items")[0].serial_no = serial_nos[0] + "\n" + serial_nos[1]
		pos.append("payments", {'mode_of_payment': 'Cash', 'account': 'Cash - _TC', 'amount': 1000, 'default': 1})

		pos.insert()
		pos.submit()

		pos_return1 = make_sales_return(pos.name)

		# partial return 1
		pos_return1.get('items')[0].qty = -1
		pos_return1.get('items')[0].serial_no = serial_nos[0]
		pos_return1.insert()
		pos_return1.submit()

		# partial return 2
		pos_return2 = make_sales_return(pos.name)
		self.assertEqual(pos_return2.get('items')[0].qty, -1)
		self.assertEqual(pos_return2.get('items')[0].serial_no, serial_nos[1])

	def test_pos_change_amount(self):
		pos = create_pos_invoice(company= "_Test Company", debit_to="Debtors - _TC",
			income_account = "Sales - _TC", expense_account = "Cost of Goods Sold - _TC", rate=105,
			cost_center = "Main - _TC", do_not_save=True)

		pos.set('payments', [])
		pos.append("payments", {'mode_of_payment': 'Bank Draft', 'account': '_Test Bank - _TC', 'amount': 50})
		pos.append("payments", {'mode_of_payment': 'Cash', 'account': 'Cash - _TC', 'amount': 60, 'default': 1})

		pos.insert()
		pos.submit()

		self.assertEqual(pos.grand_total, 105.0)
		self.assertEqual(pos.change_amount, 5.0)

	def test_without_payment(self):
		inv = create_pos_invoice(do_not_save=1)
		# Check that the invoice cannot be submitted without payments
		inv.payments = []
		self.assertRaises(frappe.ValidationError, inv.insert)

	def test_serialized_item_transaction(self):
		from erpnext.stock.doctype.stock_entry.test_stock_entry import make_serialized_item
		from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos

		se = make_serialized_item(company='_Test Company',
			target_warehouse="Stores - _TC", cost_center='Main - _TC', expense_account='Cost of Goods Sold - _TC')

		serial_nos = get_serial_nos(se.get("items")[0].serial_no)

		pos = create_pos_invoice(company='_Test Company', debit_to='Debtors - _TC',
			account_for_change_amount='Cash - _TC', warehouse='Stores - _TC', income_account='Sales - _TC',
			expense_account='Cost of Goods Sold - _TC', cost_center='Main - _TC',
			item=se.get("items")[0].item_code, rate=1000, do_not_save=1)

		pos.get("items")[0].serial_no = serial_nos[0]
		pos.append("payments", {'mode_of_payment': 'Bank Draft', 'account': '_Test Bank - _TC', 'amount': 1000})

		pos.insert()
		pos.submit()

		pos2 = create_pos_invoice(company='_Test Company', debit_to='Debtors - _TC',
			account_for_change_amount='Cash - _TC', warehouse='Stores - _TC', income_account='Sales - _TC',
			expense_account='Cost of Goods Sold - _TC', cost_center='Main - _TC',
			item=se.get("items")[0].item_code, rate=1000, do_not_save=1)

		pos2.get("items")[0].serial_no = serial_nos[0]
		pos2.append("payments", {'mode_of_payment': 'Bank Draft', 'account': '_Test Bank - _TC', 'amount': 1000})

		self.assertRaises(frappe.ValidationError, pos2.insert)

	def test_loyalty_points(self):
		from erpnext.accounts.doctype.loyalty_program.test_loyalty_program import create_records
		from erpnext.accounts.doctype.loyalty_program.loyalty_program import get_loyalty_program_details_with_points

		create_records()
		frappe.db.set_value("Customer", "Test Loyalty Customer", "loyalty_program", "Test Single Loyalty")
		before_lp_details = get_loyalty_program_details_with_points("Test Loyalty Customer", company="_Test Company", loyalty_program="Test Single Loyalty")

		inv = create_pos_invoice(customer="Test Loyalty Customer", rate=10000)

		lpe = frappe.get_doc('Loyalty Point Entry', {'invoice_type': 'POS Invoice', 'invoice': inv.name, 'customer': inv.customer})
		after_lp_details = get_loyalty_program_details_with_points(inv.customer, company=inv.company, loyalty_program=inv.loyalty_program)

		self.assertEqual(inv.get('loyalty_program'), "Test Single Loyalty")
		self.assertEqual(lpe.loyalty_points, 10)
		self.assertEqual(after_lp_details.loyalty_points, before_lp_details.loyalty_points + 10)

		inv.cancel()
		after_cancel_lp_details = get_loyalty_program_details_with_points(inv.customer, company=inv.company, loyalty_program=inv.loyalty_program)
		self.assertEqual(after_cancel_lp_details.loyalty_points, before_lp_details.loyalty_points)

	def test_loyalty_points_redeemption(self):
		from erpnext.accounts.doctype.loyalty_program.loyalty_program import get_loyalty_program_details_with_points
		# add 10 loyalty points
		create_pos_invoice(customer="Test Loyalty Customer", rate=10000)

		before_lp_details = get_loyalty_program_details_with_points("Test Loyalty Customer", company="_Test Company", loyalty_program="Test Single Loyalty")

		inv = create_pos_invoice(customer="Test Loyalty Customer", rate=10000, do_not_save=1)
		inv.redeem_loyalty_points = 1
		inv.loyalty_points = before_lp_details.loyalty_points
		inv.loyalty_amount = inv.loyalty_points * before_lp_details.conversion_factor
		inv.append("payments", {'mode_of_payment': 'Cash', 'account': 'Cash - _TC', 'amount': 10000 - inv.loyalty_amount})
		inv.paid_amount = 10000
		inv.submit()

		after_redeem_lp_details = get_loyalty_program_details_with_points(inv.customer, company=inv.company, loyalty_program=inv.loyalty_program)
		self.assertEqual(after_redeem_lp_details.loyalty_points, 9)

	def test_merging_into_sales_invoice_with_discount(self):
		from erpnext.accounts.doctype.pos_closing_entry.test_pos_closing_entry import init_user_and_profile
		from erpnext.accounts.doctype.pos_invoice_merge_log.pos_invoice_merge_log import consolidate_pos_invoices

		frappe.db.sql("delete from `tabPOS Invoice`")
		test_user, pos_profile = init_user_and_profile()
		pos_inv = create_pos_invoice(rate=300, additional_discount_percentage=10, do_not_submit=1)
		pos_inv.append('payments', {
			'mode_of_payment': 'Cash', 'account': 'Cash - _TC', 'amount': 270
		})
		pos_inv.submit()

		pos_inv2 = create_pos_invoice(rate=3200, do_not_submit=1)
		pos_inv2.append('payments', {
			'mode_of_payment': 'Cash', 'account': 'Cash - _TC', 'amount': 3200
		})
		pos_inv2.submit()

		consolidate_pos_invoices()

		pos_inv.load_from_db()
		rounded_total = frappe.db.get_value("Sales Invoice", pos_inv.consolidated_invoice, "rounded_total")
		self.assertEqual(rounded_total, 3470)
		frappe.set_user("Administrator")

	def test_merging_into_sales_invoice_with_discount_and_inclusive_tax(self):
		from erpnext.accounts.doctype.pos_closing_entry.test_pos_closing_entry import init_user_and_profile
		from erpnext.accounts.doctype.pos_invoice_merge_log.pos_invoice_merge_log import consolidate_pos_invoices

		frappe.db.sql("delete from `tabPOS Invoice`")
		test_user, pos_profile = init_user_and_profile()
		pos_inv = create_pos_invoice(rate=300, do_not_submit=1)
		pos_inv.append('payments', {
			'mode_of_payment': 'Cash', 'account': 'Cash - _TC', 'amount': 300
		})
		pos_inv.append('taxes', {
			"charge_type": "On Net Total",
			"account_head": "_Test Account Service Tax - _TC",
			"cost_center": "_Test Cost Center - _TC",
			"description": "Service Tax",
			"rate": 14,
			'included_in_print_rate': 1
		})
		pos_inv.submit()

		pos_inv2 = create_pos_invoice(rate=300, qty=2, do_not_submit=1)
		pos_inv2.additional_discount_percentage = 10
		pos_inv2.append('payments', {
			'mode_of_payment': 'Cash', 'account': 'Cash - _TC', 'amount': 540
		})
		pos_inv2.append('taxes', {
			"charge_type": "On Net Total",
			"account_head": "_Test Account Service Tax - _TC",
			"cost_center": "_Test Cost Center - _TC",
			"description": "Service Tax",
			"rate": 14,
			'included_in_print_rate': 1
		})
		pos_inv2.submit()

		consolidate_pos_invoices()

		pos_inv.load_from_db()
		rounded_total = frappe.db.get_value("Sales Invoice", pos_inv.consolidated_invoice, "rounded_total")
		self.assertEqual(rounded_total, 840)
		frappe.set_user("Administrator")

	def test_merging_with_validate_selling_price(self):
		from erpnext.accounts.doctype.pos_closing_entry.test_pos_closing_entry import init_user_and_profile
		from erpnext.accounts.doctype.pos_invoice_merge_log.pos_invoice_merge_log import consolidate_pos_invoices

		if not frappe.db.get_single_value("Selling Settings", "validate_selling_price"):
			frappe.db.set_value("Selling Settings", "Selling Settings", "validate_selling_price", 1)

		make_purchase_receipt(item_code="_Test Item", warehouse="_Test Warehouse - _TC", qty=1, rate=300)
		frappe.db.sql("delete from `tabPOS Invoice`")
		test_user, pos_profile = init_user_and_profile()
		pos_inv = create_pos_invoice(rate=300, do_not_submit=1)
		pos_inv.append('payments', {
			'mode_of_payment': 'Cash', 'account': 'Cash - _TC', 'amount': 300
		})
		pos_inv.append('taxes', {
			"charge_type": "On Net Total",
			"account_head": "_Test Account Service Tax - _TC",
			"cost_center": "_Test Cost Center - _TC",
			"description": "Service Tax",
			"rate": 14,
			'included_in_print_rate': 1
		})
		self.assertRaises(frappe.ValidationError, pos_inv.submit)

		pos_inv2 = create_pos_invoice(rate=400, do_not_submit=1)
		pos_inv2.append('payments', {
			'mode_of_payment': 'Cash', 'account': 'Cash - _TC', 'amount': 400
		})
		pos_inv2.append('taxes', {
			"charge_type": "On Net Total",
			"account_head": "_Test Account Service Tax - _TC",
			"cost_center": "_Test Cost Center - _TC",
			"description": "Service Tax",
			"rate": 14,
			'included_in_print_rate': 1
		})
		pos_inv2.submit()

		consolidate_pos_invoices()

		pos_inv2.load_from_db()
		rounded_total = frappe.db.get_value("Sales Invoice", pos_inv2.consolidated_invoice, "rounded_total")
		self.assertEqual(rounded_total, 400)
		frappe.set_user("Administrator")
		frappe.db.set_value("Selling Settings", "Selling Settings", "validate_selling_price", 0)

def create_pos_invoice(**args):
	args = frappe._dict(args)
	pos_profile = None
	if not args.pos_profile:
		pos_profile = make_pos_profile()
		pos_profile.save()

	pos_inv = frappe.new_doc("POS Invoice")
	pos_inv.update(args)
	pos_inv.update_stock = 1
	pos_inv.is_pos = 1
	pos_inv.pos_profile = args.pos_profile or pos_profile.name

	if args.posting_date:
		pos_inv.set_posting_time = 1
	pos_inv.posting_date = args.posting_date or frappe.utils.nowdate()

	pos_inv.company = args.company or "_Test Company"
	pos_inv.customer = args.customer or "_Test Customer"
	pos_inv.debit_to = args.debit_to or "Debtors - _TC"
	pos_inv.is_return = args.is_return
	pos_inv.return_against = args.return_against
	pos_inv.currency=args.currency or "INR"
	pos_inv.conversion_rate = args.conversion_rate or 1
	pos_inv.account_for_change_amount = args.account_for_change_amount or "Cash - _TC"

	pos_inv.set_missing_values()

	pos_inv.append("items", {
		"item_code": args.item or args.item_code or "_Test Item",
		"warehouse": args.warehouse or "_Test Warehouse - _TC",
		"qty": args.qty or 1,
		"rate": args.rate if args.get("rate") is not None else 100,
		"income_account": args.income_account or "Sales - _TC",
		"expense_account": args.expense_account or "Cost of Goods Sold - _TC",
		"cost_center": args.cost_center or "_Test Cost Center - _TC",
		"serial_no": args.serial_no
	})

	if not args.do_not_save:
		pos_inv.insert()
		if not args.do_not_submit:
			pos_inv.submit()
		else:
			pos_inv.payment_schedule = []
	else:
		pos_inv.payment_schedule = []

	return pos_inv