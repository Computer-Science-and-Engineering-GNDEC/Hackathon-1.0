# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe.utils import cint, flt, cstr, get_link_to_form, today, getdate
from frappe import _
import frappe.defaults
from collections import defaultdict
from erpnext.accounts.utils import get_fiscal_year, check_if_stock_and_account_balance_synced
from erpnext.accounts.general_ledger import make_gl_entries, make_reverse_gl_entries, process_gl_map
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.stock.stock_ledger import get_valuation_rate
from erpnext.stock import get_warehouse_account_map

class QualityInspectionRequiredError(frappe.ValidationError): pass
class QualityInspectionRejectedError(frappe.ValidationError): pass
class QualityInspectionNotSubmittedError(frappe.ValidationError): pass

class StockController(AccountsController):
	def validate(self):
		super(StockController, self).validate()
		if not self.get('is_return'):
			self.validate_inspection()
		self.validate_serialized_batch()
		self.validate_customer_provided_item()
		self.set_rate_of_stock_uom()
		self.validate_internal_transfer()
		self.validate_putaway_capacity()

	def make_gl_entries(self, gl_entries=None, from_repost=False):
		if self.docstatus == 2:
			make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)

		if cint(erpnext.is_perpetual_inventory_enabled(self.company)):
			warehouse_account = get_warehouse_account_map(self.company)

			if self.docstatus==1:
				if not gl_entries:
					gl_entries = self.get_gl_entries(warehouse_account)
				make_gl_entries(gl_entries, from_repost=from_repost)

		elif self.doctype in ['Purchase Receipt', 'Purchase Invoice'] and self.docstatus == 1:
			gl_entries = []
			gl_entries = self.get_asset_gl_entry(gl_entries)
			make_gl_entries(gl_entries, from_repost=from_repost)

	def validate_serialized_batch(self):
		from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos
		for d in self.get("items"):
			if hasattr(d, 'serial_no') and hasattr(d, 'batch_no') and d.serial_no and d.batch_no:
				serial_nos = get_serial_nos(d.serial_no)
				for serial_no_data in frappe.get_all("Serial No",
					filters={"name": ("in", serial_nos)}, fields=["batch_no", "name"]):
					if serial_no_data.batch_no != d.batch_no:
						frappe.throw(_("Row #{0}: Serial No {1} does not belong to Batch {2}")
							.format(d.idx, serial_no_data.name, d.batch_no))

			if flt(d.qty) > 0.0 and d.get("batch_no") and self.get("posting_date") and self.docstatus < 2:
				expiry_date = frappe.get_cached_value("Batch", d.get("batch_no"), "expiry_date")

				if expiry_date and getdate(expiry_date) < getdate(self.posting_date):
					frappe.throw(_("Row #{0}: The batch {1} has already expired.")
						.format(d.idx, get_link_to_form("Batch", d.get("batch_no"))))

	def get_gl_entries(self, warehouse_account=None, default_expense_account=None,
			default_cost_center=None):

		if not warehouse_account:
			warehouse_account = get_warehouse_account_map(self.company)

		sle_map = self.get_stock_ledger_details()
		voucher_details = self.get_voucher_details(default_expense_account, default_cost_center, sle_map)

		gl_list = []
		warehouse_with_no_account = []
		precision = self.get_debit_field_precision()
		for item_row in voucher_details:

			sle_list = sle_map.get(item_row.name)
			if sle_list:
				for sle in sle_list:
					if warehouse_account.get(sle.warehouse):
						# from warehouse account

						self.check_expense_account(item_row)

						# If the item does not have the allow zero valuation rate flag set
						# and ( valuation rate not mentioned in an incoming entry
						# or incoming entry not found while delivering the item),
						# try to pick valuation rate from previous sle or Item master and update in SLE
						# Otherwise, throw an exception

						if not sle.stock_value_difference and self.doctype != "Stock Reconciliation" \
							and not item_row.get("allow_zero_valuation_rate"):

							sle = self.update_stock_ledger_entries(sle)

						# expense account/ target_warehouse / source_warehouse
						if item_row.get('target_warehouse'):
							warehouse = item_row.get('target_warehouse')
							expense_account = warehouse_account[warehouse]["account"]
						else:
							expense_account = item_row.expense_account

						gl_list.append(self.get_gl_dict({
							"account": warehouse_account[sle.warehouse]["account"],
							"against": expense_account,
							"cost_center": item_row.cost_center,
							"project": item_row.project or self.get('project'),
							"remarks": self.get("remarks") or "Accounting Entry for Stock",
							"debit": flt(sle.stock_value_difference, precision),
							"is_opening": item_row.get("is_opening") or self.get("is_opening") or "No",
						}, warehouse_account[sle.warehouse]["account_currency"], item=item_row))

						gl_list.append(self.get_gl_dict({
							"account": expense_account,
							"against": warehouse_account[sle.warehouse]["account"],
							"cost_center": item_row.cost_center,
							"project": item_row.project or self.get('project'),
							"remarks": self.get("remarks") or "Accounting Entry for Stock",
							"credit": flt(sle.stock_value_difference, precision),
							"project": item_row.get("project") or self.get("project"),
							"is_opening": item_row.get("is_opening") or self.get("is_opening") or "No"
						}, item=item_row))
					elif sle.warehouse not in warehouse_with_no_account:
						warehouse_with_no_account.append(sle.warehouse)

		if warehouse_with_no_account:
			for wh in warehouse_with_no_account:
				if frappe.db.get_value("Warehouse", wh, "company"):
					frappe.throw(_("Warehouse {0} is not linked to any account, please mention the account in the warehouse record or set default inventory account in company {1}.").format(wh, self.company))

		return process_gl_map(gl_list, precision=precision)

	def get_debit_field_precision(self):
		if not frappe.flags.debit_field_precision:
			frappe.flags.debit_field_precision = frappe.get_precision("GL Entry", "debit_in_account_currency")

		return frappe.flags.debit_field_precision

	def update_stock_ledger_entries(self, sle):
		sle.valuation_rate = get_valuation_rate(sle.item_code, sle.warehouse,
			self.doctype, self.name, currency=self.company_currency, company=self.company)

		sle.stock_value = flt(sle.qty_after_transaction) * flt(sle.valuation_rate)
		sle.stock_value_difference = flt(sle.actual_qty) * flt(sle.valuation_rate)

		if sle.name:
			frappe.db.sql("""
				update
					`tabStock Ledger Entry`
				set
					stock_value = %(stock_value)s,
					valuation_rate = %(valuation_rate)s,
					stock_value_difference = %(stock_value_difference)s
				where
					name = %(name)s""", (sle))

		return sle

	def get_voucher_details(self, default_expense_account, default_cost_center, sle_map):
		if self.doctype == "Stock Reconciliation":
			reconciliation_purpose = frappe.db.get_value(self.doctype, self.name, "purpose")
			is_opening = "Yes" if reconciliation_purpose == "Opening Stock" else "No"
			details = []
			for voucher_detail_no in sle_map:
				details.append(frappe._dict({
					"name": voucher_detail_no,
					"expense_account": default_expense_account,
					"cost_center": default_cost_center,
					"is_opening": is_opening
				}))
			return details
		else:
			details = self.get("items")

			if default_expense_account or default_cost_center:
				for d in details:
					if default_expense_account and not d.get("expense_account"):
						d.expense_account = default_expense_account
					if default_cost_center and not d.get("cost_center"):
						d.cost_center = default_cost_center

			return details

	def get_items_and_warehouses(self):
		items, warehouses = [], []

		if hasattr(self, "items"):
			item_doclist = self.get("items")
		elif self.doctype == "Stock Reconciliation":
			import json
			item_doclist = []
			data = json.loads(self.reconciliation_json)
			for row in data[data.index(self.head_row)+1:]:
				d = frappe._dict(zip(["item_code", "warehouse", "qty", "valuation_rate"], row))
				item_doclist.append(d)

		if item_doclist:
			for d in item_doclist:
				if d.item_code and d.item_code not in items:
					items.append(d.item_code)

				if d.get("warehouse") and d.warehouse not in warehouses:
					warehouses.append(d.warehouse)

				if self.doctype == "Stock Entry":
					if d.get("s_warehouse") and d.s_warehouse not in warehouses:
						warehouses.append(d.s_warehouse)
					if d.get("t_warehouse") and d.t_warehouse not in warehouses:
						warehouses.append(d.t_warehouse)

		return items, warehouses

	def get_stock_ledger_details(self):
		stock_ledger = {}
		stock_ledger_entries = frappe.db.sql("""
			select
				name, warehouse, stock_value_difference, valuation_rate,
				voucher_detail_no, item_code, posting_date, posting_time,
				actual_qty, qty_after_transaction
			from
				`tabStock Ledger Entry`
			where
				voucher_type=%s and voucher_no=%s
		""", (self.doctype, self.name), as_dict=True)

		for sle in stock_ledger_entries:
			stock_ledger.setdefault(sle.voucher_detail_no, []).append(sle)
		return stock_ledger

	def make_batches(self, warehouse_field):
		'''Create batches if required. Called before submit'''
		for d in self.items:
			if d.get(warehouse_field) and not d.batch_no:
				has_batch_no, create_new_batch = frappe.db.get_value('Item', d.item_code, ['has_batch_no', 'create_new_batch'])
				if has_batch_no and create_new_batch:
					d.batch_no = frappe.get_doc(dict(
						doctype='Batch',
						item=d.item_code,
						supplier=getattr(self, 'supplier', None),
						reference_doctype=self.doctype,
						reference_name=self.name)).insert().name

	def check_expense_account(self, item):
		if not item.get("expense_account"):
			msg = _("Please set an Expense Account in the Items table")
			frappe.throw(_("Row #{0}: Expense Account not set for the Item {1}. {2}")
				.format(item.idx, frappe.bold(item.item_code), msg), title=_("Expense Account Missing"))

		else:
			is_expense_account = frappe.get_cached_value("Account",
				item.get("expense_account"), "report_type")=="Profit and Loss"
			if self.doctype not in ("Purchase Receipt", "Purchase Invoice", "Stock Reconciliation", "Stock Entry") and not is_expense_account:
				frappe.throw(_("Expense / Difference account ({0}) must be a 'Profit or Loss' account")
					.format(item.get("expense_account")))
			if is_expense_account and not item.get("cost_center"):
				frappe.throw(_("{0} {1}: Cost Center is mandatory for Item {2}").format(
					_(self.doctype), self.name, item.get("item_code")))

	def delete_auto_created_batches(self):
		for d in self.items:
			if not d.batch_no: continue

			serial_nos = [sr.name for sr in frappe.get_all("Serial No",
				{'batch_no': d.batch_no, 'status': 'Inactive'})]

			if serial_nos:
				frappe.db.set_value("Serial No", { 'name': ['in', serial_nos] }, "batch_no", None)

			d.batch_no = None
			d.db_set("batch_no", None)

		for data in frappe.get_all("Batch",
			{'reference_name': self.name, 'reference_doctype': self.doctype}):
			frappe.delete_doc("Batch", data.name)

	def get_sl_entries(self, d, args):
		sl_dict = frappe._dict({
			"item_code": d.get("item_code", None),
			"warehouse": d.get("warehouse", None),
			"posting_date": self.posting_date,
			"posting_time": self.posting_time,
			'fiscal_year': get_fiscal_year(self.posting_date, company=self.company)[0],
			"voucher_type": self.doctype,
			"voucher_no": self.name,
			"voucher_detail_no": d.name,
			"actual_qty": (self.docstatus==1 and 1 or -1)*flt(d.get("stock_qty")),
			"stock_uom": frappe.db.get_value("Item", args.get("item_code") or d.get("item_code"), "stock_uom"),
			"incoming_rate": 0,
			"company": self.company,
			"batch_no": cstr(d.get("batch_no")).strip(),
			"serial_no": d.get("serial_no"),
			"project": d.get("project") or self.get('project'),
			"is_cancelled": 1 if self.docstatus==2 else 0
		})

		sl_dict.update(args)
		return sl_dict

	def make_sl_entries(self, sl_entries, allow_negative_stock=False,
			via_landed_cost_voucher=False):
		from erpnext.stock.stock_ledger import make_sl_entries
		make_sl_entries(sl_entries, allow_negative_stock, via_landed_cost_voucher)

	def make_gl_entries_on_cancel(self):
		if frappe.db.sql("""select name from `tabGL Entry` where voucher_type=%s
			and voucher_no=%s""", (self.doctype, self.name)):
				self.make_gl_entries()

	def get_serialized_items(self):
		serialized_items = []
		item_codes = list(set([d.item_code for d in self.get("items")]))
		if item_codes:
			serialized_items = frappe.db.sql_list("""select name from `tabItem`
				where has_serial_no=1 and name in ({})""".format(", ".join(["%s"]*len(item_codes))),
				tuple(item_codes))

		return serialized_items

	def validate_warehouse(self):
		from erpnext.stock.utils import validate_warehouse_company, validate_disabled_warehouse

		warehouses = list(set([d.warehouse for d in
			self.get("items") if getattr(d, "warehouse", None)]))

		target_warehouses = list(set([d.target_warehouse for d in
			self.get("items") if getattr(d, "target_warehouse", None)]))

		warehouses.extend(target_warehouses)

		from_warehouse = list(set([d.from_warehouse for d in
			self.get("items") if getattr(d, "from_warehouse", None)]))

		warehouses.extend(from_warehouse)

		for w in warehouses:
			validate_disabled_warehouse(w)
			validate_warehouse_company(w, self.company)

	def update_billing_percentage(self, update_modified=True):
		target_ref_field = "amount"
		if self.doctype == "Delivery Note":
			target_ref_field = "amount - (returned_qty * rate)"

		self._update_percent_field({
			"target_dt": self.doctype + " Item",
			"target_parent_dt": self.doctype,
			"target_parent_field": "per_billed",
			"target_ref_field": target_ref_field,
			"target_field": "billed_amt",
			"name": self.name,
		}, update_modified)

	def validate_inspection(self):
		'''Checks if quality inspection is set for Items that require inspection.
		On submit, throw an exception'''
		inspection_required_fieldname = None
		if self.doctype in ["Purchase Receipt", "Purchase Invoice"]:
			inspection_required_fieldname = "inspection_required_before_purchase"
		elif self.doctype in ["Delivery Note", "Sales Invoice"]:
			inspection_required_fieldname = "inspection_required_before_delivery"

		if ((not inspection_required_fieldname and self.doctype != "Stock Entry") or
			(self.doctype == "Stock Entry" and not self.inspection_required) or
			(self.doctype in ["Sales Invoice", "Purchase Invoice"] and not self.update_stock)):
				return

		for d in self.get('items'):
			qa_required = False
			if (inspection_required_fieldname and not d.quality_inspection and
				frappe.db.get_value("Item", d.item_code, inspection_required_fieldname)):
				qa_required = True
			elif self.doctype == "Stock Entry" and not d.quality_inspection and d.t_warehouse:
				qa_required = True
			if self.docstatus == 1 and d.quality_inspection:
				qa_doc = frappe.get_doc("Quality Inspection", d.quality_inspection)
				if qa_doc.docstatus == 0:
					link = frappe.utils.get_link_to_form('Quality Inspection', d.quality_inspection)
					frappe.throw(_("Quality Inspection: {0} is not submitted for the item: {1} in row {2}").format(link, d.item_code, d.idx), QualityInspectionNotSubmittedError)

				qa_failed = any([r.status=="Rejected" for r in qa_doc.readings])
				if qa_failed:
					frappe.throw(_("Row {0}: Quality Inspection rejected for item {1}")
						.format(d.idx, d.item_code), QualityInspectionRejectedError)
			elif qa_required :
				action = frappe.get_doc('Stock Settings').action_if_quality_inspection_is_not_submitted
				if self.docstatus==1 and action == 'Stop':
					frappe.throw(_("Quality Inspection required for Item {0} to submit").format(frappe.bold(d.item_code)),
						exc=QualityInspectionRequiredError)
				else:
					frappe.msgprint(_("Create Quality Inspection for Item {0}").format(frappe.bold(d.item_code)))

	def update_blanket_order(self):
		blanket_orders = list(set([d.blanket_order for d in self.items if d.blanket_order]))
		for blanket_order in blanket_orders:
			frappe.get_doc("Blanket Order", blanket_order).update_ordered_qty()

	def validate_customer_provided_item(self):
		for d in self.get('items'):
			# Customer Provided parts will have zero valuation rate
			if frappe.db.get_value('Item', d.item_code, 'is_customer_provided_item'):
				d.allow_zero_valuation_rate = 1

	def set_rate_of_stock_uom(self):
		if self.doctype in ["Purchase Receipt", "Purchase Invoice", "Purchase Order", "Sales Invoice", "Sales Order", "Delivery Note", "Quotation"]:
			for d in self.get("items"):
				d.stock_uom_rate = d.rate / d.conversion_factor

	def validate_internal_transfer(self):
		if self.doctype in ('Sales Invoice', 'Delivery Note', 'Purchase Invoice', 'Purchase Receipt') \
			and self.is_internal_transfer():
			self.validate_in_transit_warehouses()
			self.validate_multi_currency()
			self.validate_packed_items()

	def validate_in_transit_warehouses(self):
		if (self.doctype == 'Sales Invoice' and self.get('update_stock')) or self.doctype == 'Delivery Note':
			for item in self.get('items'):
				if not item.target_warehouse:
					frappe.throw(_("Row {0}: Target Warehouse is mandatory for internal transfers").format(item.idx))

		if (self.doctype == 'Purchase Invoice' and self.get('update_stock')) or self.doctype == 'Purchase Receipt':
			for item in self.get('items'):
				if not item.from_warehouse:
					frappe.throw(_("Row {0}: From Warehouse is mandatory for internal transfers").format(item.idx))

	def validate_multi_currency(self):
		if self.currency != self.company_currency:
			frappe.throw(_("Internal transfers can only be done in company's default currency"))

	def validate_packed_items(self):
		if self.doctype in ('Sales Invoice', 'Delivery Note Item') and self.get('packed_items'):
			frappe.throw(_("Packed Items cannot be transferred internally"))

	def validate_putaway_capacity(self):
		# if over receipt is attempted while 'apply putaway rule' is disabled
		# and if rule was applied on the transaction, validate it.
		from erpnext.stock.doctype.putaway_rule.putaway_rule import get_available_putaway_capacity
		valid_doctype = self.doctype in ("Purchase Receipt", "Stock Entry", "Purchase Invoice",
			"Stock Reconciliation")

		if self.doctype == "Purchase Invoice" and self.get("update_stock") == 0:
			valid_doctype = False

		if valid_doctype:
			rule_map = defaultdict(dict)
			for item in self.get("items"):
				warehouse_field = "t_warehouse" if self.doctype == "Stock Entry" else "warehouse"
				rule = frappe.db.get_value("Putaway Rule",
					{
						"item_code": item.get("item_code"),
						"warehouse": item.get(warehouse_field)
					},
					["name", "disable"], as_dict=True)
				if rule:
					if rule.get("disabled"): continue # dont validate for disabled rule

					if self.doctype == "Stock Reconciliation":
						stock_qty = flt(item.qty)
					else:
						stock_qty = flt(item.transfer_qty) if self.doctype == "Stock Entry" else flt(item.stock_qty)

					rule_name = rule.get("name")
					if not rule_map[rule_name]:
						rule_map[rule_name]["warehouse"] = item.get(warehouse_field)
						rule_map[rule_name]["item"] = item.get("item_code")
						rule_map[rule_name]["qty_put"] = 0
						rule_map[rule_name]["capacity"] = get_available_putaway_capacity(rule_name)
					rule_map[rule_name]["qty_put"] += flt(stock_qty)

			for rule, values in rule_map.items():
				if flt(values["qty_put"]) > flt(values["capacity"]):
					message = self.prepare_over_receipt_message(rule, values)
					frappe.throw(msg=message, title=_("Over Receipt"))

	def prepare_over_receipt_message(self, rule, values):
		message = _("{0} qty of Item {1} is being received into Warehouse {2} with capacity {3}.") \
			.format(
				frappe.bold(values["qty_put"]), frappe.bold(values["item"]),
				frappe.bold(values["warehouse"]), frappe.bold(values["capacity"])
			)
		message += "<br><br>"
		rule_link = frappe.utils.get_link_to_form("Putaway Rule", rule)
		message += _(" Please adjust the qty or edit {0} to proceed.").format(rule_link)
		return message

	def repost_future_sle_and_gle(self):
		args = frappe._dict({
			"posting_date": self.posting_date,
			"posting_time": self.posting_time,
			"voucher_type": self.doctype,
			"voucher_no": self.name,
			"company": self.company
		})
		if check_if_future_sle_exists(args):
			create_repost_item_valuation_entry(args)
		elif not is_reposting_pending():
			check_if_stock_and_account_balance_synced(self.posting_date,
				self.company, self.doctype, self.name)

def is_reposting_pending():
	return frappe.db.exists("Repost Item Valuation",
		{'docstatus': 1, 'status': ['in', ['Queued','In Progress']]})


def check_if_future_sle_exists(args):
	sl_entries = frappe.db.get_all("Stock Ledger Entry",
		filters={"voucher_type": args.voucher_type, "voucher_no": args.voucher_no},
		fields=["item_code", "warehouse"],
		order_by="creation asc")

	distinct_item_warehouses = list(set([(d.item_code, d.warehouse) for d in sl_entries]))

	sle_exists = False
	for item_code, warehouse in distinct_item_warehouses:
		args.update({
			"item_code": item_code,
			"warehouse": warehouse
		})
		if get_sle(args):
			sle_exists = True
			break
	return sle_exists

def get_sle(args):
	return frappe.db.sql("""
		select name
		from `tabStock Ledger Entry`
		where
			item_code=%(item_code)s
			and warehouse=%(warehouse)s
			and timestamp(posting_date, posting_time) >= timestamp(%(posting_date)s, %(posting_time)s)
			and voucher_no != %(voucher_no)s
			and is_cancelled = 0
		limit 1
	""", args)

def create_repost_item_valuation_entry(args):
	args = frappe._dict(args)
	repost_entry = frappe.new_doc("Repost Item Valuation")
	repost_entry.based_on = args.based_on
	if not args.based_on:
		repost_entry.based_on = 'Transaction' if args.voucher_no else "Item and Warehouse"
	repost_entry.voucher_type = args.voucher_type
	repost_entry.voucher_no = args.voucher_no
	repost_entry.item_code = args.item_code
	repost_entry.warehouse = args.warehouse
	repost_entry.posting_date = args.posting_date
	repost_entry.posting_time = args.posting_time
	repost_entry.company = args.company
	repost_entry.allow_zero_rate = args.allow_zero_rate
	repost_entry.flags.ignore_links = True
	repost_entry.save()
	repost_entry.submit()