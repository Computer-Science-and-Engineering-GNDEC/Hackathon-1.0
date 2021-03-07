# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import frappe, erpnext
from frappe.utils import cint, cstr, formatdate, flt, getdate, nowdate, get_link_to_form
from frappe import _, throw
import frappe.defaults

from erpnext.assets.doctype.asset_category.asset_category import get_asset_category_account
from erpnext.controllers.buying_controller import BuyingController
from erpnext.accounts.party import get_party_account, get_due_date
from erpnext.accounts.utils import get_account_currency, get_fiscal_year
from erpnext.stock.doctype.purchase_receipt.purchase_receipt import update_billed_amount_based_on_po
from erpnext.stock import get_warehouse_account_map
from erpnext.accounts.general_ledger import make_gl_entries, merge_similar_entries, make_reverse_gl_entries
from erpnext.accounts.doctype.gl_entry.gl_entry import update_outstanding_amt
from erpnext.buying.utils import check_on_hold_or_closed_status
from erpnext.accounts.general_ledger import get_round_off_account_and_cost_center
from erpnext.assets.doctype.asset.asset import get_asset_account, is_cwip_accounting_enabled
from frappe.model.mapper import get_mapped_doc
from six import iteritems
from erpnext.accounts.doctype.sales_invoice.sales_invoice import validate_inter_company_party, update_linked_doc,\
	unlink_inter_company_doc
from erpnext.accounts.doctype.tax_withholding_category.tax_withholding_category import get_party_tax_withholding_details
from erpnext.accounts.deferred_revenue import validate_service_stop_date
from erpnext.stock.doctype.purchase_receipt.purchase_receipt import get_item_account_wise_additional_cost

form_grid_templates = {
	"items": "templates/form_grid/item_grid.html"
}

class PurchaseInvoice(BuyingController):
	def __init__(self, *args, **kwargs):
		super(PurchaseInvoice, self).__init__(*args, **kwargs)
		self.status_updater = [{
			'source_dt': 'Purchase Invoice Item',
			'target_dt': 'Purchase Order Item',
			'join_field': 'po_detail',
			'target_field': 'billed_amt',
			'target_parent_dt': 'Purchase Order',
			'target_parent_field': 'per_billed',
			'target_ref_field': 'amount',
			'source_field': 'amount',
			'percent_join_field': 'purchase_order',
			'overflow_type': 'billing'
		}]

	def onload(self):
		super(PurchaseInvoice, self).onload()
		supplier_tds = frappe.db.get_value("Supplier", self.supplier, "tax_withholding_category")
		self.set_onload("supplier_tds", supplier_tds)

	def before_save(self):
		if not self.on_hold:
			self.release_date = ''


	def invoice_is_blocked(self):
		return self.on_hold and (not self.release_date or self.release_date > getdate(nowdate()))

	def validate(self):
		if not self.is_opening:
			self.is_opening = 'No'

		self.validate_posting_time()

		super(PurchaseInvoice, self).validate()

		# apply tax withholding only if checked and applicable
		self.set_tax_withholding()

		if not self.is_return:
			self.po_required()
			self.pr_required()
			self.validate_supplier_invoice()

		# validate cash purchase
		if (self.is_paid == 1):
			self.validate_cash()

		# validate service stop date to lie in between start and end date
		validate_service_stop_date(self)

		if self._action=="submit" and self.update_stock:
			self.make_batches('warehouse')

		self.validate_release_date()
		self.check_conversion_rate()
		self.validate_credit_to_acc()
		self.clear_unallocated_advances("Purchase Invoice Advance", "advances")
		self.check_on_hold_or_closed_status()
		self.validate_with_previous_doc()
		self.validate_uom_is_integer("uom", "qty")
		self.validate_uom_is_integer("stock_uom", "stock_qty")
		self.set_expense_account(for_validate=True)
		self.set_against_expense_account()
		self.validate_write_off_account()
		self.validate_multiple_billing("Purchase Receipt", "pr_detail", "amount", "items")
		self.create_remarks()
		self.set_status()
		self.validate_purchase_receipt_if_update_stock()
		validate_inter_company_party(self.doctype, self.supplier, self.company, self.inter_company_invoice_reference)

	def validate_release_date(self):
		if self.release_date and getdate(nowdate()) >= getdate(self.release_date):
			frappe.throw(_('Release date must be in the future'))

	def validate_cash(self):
		if not self.cash_bank_account and flt(self.paid_amount):
			frappe.throw(_("Cash or Bank Account is mandatory for making payment entry"))

		if (flt(self.paid_amount) + flt(self.write_off_amount)
			- flt(self.get("rounded_total") or self.grand_total)
			> 1/(10**(self.precision("base_grand_total") + 1))):

			frappe.throw(_("""Paid amount + Write Off Amount can not be greater than Grand Total"""))

	def create_remarks(self):
		if not self.remarks:
			if self.bill_no and self.bill_date:
				self.remarks = _("Against Supplier Invoice {0} dated {1}").format(self.bill_no,
					formatdate(self.bill_date))
			else:
				self.remarks = _("No Remarks")

	def set_missing_values(self, for_validate=False):
		if not self.credit_to:
			self.credit_to = get_party_account("Supplier", self.supplier, self.company)
			self.party_account_currency = frappe.db.get_value("Account", self.credit_to, "account_currency", cache=True)
		if not self.due_date:
			self.due_date = get_due_date(self.posting_date, "Supplier", self.supplier, self.company,  self.bill_date)

		tds_category = frappe.db.get_value("Supplier", self.supplier, "tax_withholding_category")
		if tds_category and not for_validate:
			self.apply_tds = 1
			self.tax_withholding_category = tds_category

		super(PurchaseInvoice, self).set_missing_values(for_validate)

	def check_conversion_rate(self):
		default_currency = erpnext.get_company_currency(self.company)
		if not default_currency:
			throw(_('Please enter default currency in Company Master'))
		if (self.currency == default_currency and flt(self.conversion_rate) != 1.00) or not self.conversion_rate or (self.currency != default_currency and flt(self.conversion_rate) == 1.00):
			throw(_("Conversion rate cannot be 0 or 1"))

	def validate_credit_to_acc(self):
		if not self.credit_to:
			self.credit_to = get_party_account("Supplier", self.supplier, self.company)
			if not self.credit_to:
				self.raise_missing_debit_credit_account_error("Supplier", self.supplier)

		account = frappe.db.get_value("Account", self.credit_to,
			["account_type", "report_type", "account_currency"], as_dict=True)

		if account.report_type != "Balance Sheet":
			frappe.throw(
				_("Please ensure {} account is a Balance Sheet account. You can change the parent account to a Balance Sheet account or select a different account.")
				.format(frappe.bold("Credit To")), title=_("Invalid Account")
			)

		if self.supplier and account.account_type != "Payable":
			frappe.throw(
				_("Please ensure {} account is a Payable account. Change the account type to Payable or select a different account.")
				.format(frappe.bold("Credit To")), title=_("Invalid Account")
			)

		self.party_account_currency = account.account_currency

	def check_on_hold_or_closed_status(self):
		check_list = []

		for d in self.get('items'):
			if d.purchase_order and not d.purchase_order in check_list and not d.purchase_receipt:
				check_list.append(d.purchase_order)
				check_on_hold_or_closed_status('Purchase Order', d.purchase_order)

	def validate_with_previous_doc(self):
		super(PurchaseInvoice, self).validate_with_previous_doc({
			"Purchase Order": {
				"ref_dn_field": "purchase_order",
				"compare_fields": [["supplier", "="], ["company", "="], ["currency", "="]],
			},
			"Purchase Order Item": {
				"ref_dn_field": "po_detail",
				"compare_fields": [["project", "="], ["item_code", "="], ["uom", "="]],
				"is_child_table": True,
				"allow_duplicate_prev_row_id": True
			},
			"Purchase Receipt": {
				"ref_dn_field": "purchase_receipt",
				"compare_fields": [["supplier", "="], ["company", "="], ["currency", "="]],
			},
			"Purchase Receipt Item": {
				"ref_dn_field": "pr_detail",
				"compare_fields": [["project", "="], ["item_code", "="], ["uom", "="]],
				"is_child_table": True
			}
		})

		if cint(frappe.db.get_single_value('Buying Settings', 'maintain_same_rate')) and not self.is_return:
			self.validate_rate_with_reference_doc([
				["Purchase Order", "purchase_order", "po_detail"],
				["Purchase Receipt", "purchase_receipt", "pr_detail"]
			])

	def validate_warehouse(self, for_validate=True):
		if self.update_stock and for_validate:
			for d in self.get('items'):
				if not d.warehouse:
					frappe.throw(_("Warehouse required at Row No {0}, please set default warehouse for the item {1} for the company {2}").
						format(d.idx, d.item_code, self.company))

		super(PurchaseInvoice, self).validate_warehouse()

	def validate_item_code(self):
		for d in self.get('items'):
			if not d.item_code:
				frappe.msgprint(_("Item Code required at Row No {0}").format(d.idx), raise_exception=True)

	def set_expense_account(self, for_validate=False):
		auto_accounting_for_stock = erpnext.is_perpetual_inventory_enabled(self.company)

		if auto_accounting_for_stock:
			stock_not_billed_account = self.get_company_default("stock_received_but_not_billed")
			stock_items = self.get_stock_items()

		asset_items = [d.is_fixed_asset for d in self.items if d.is_fixed_asset]
		if len(asset_items) > 0:
			asset_received_but_not_billed = self.get_company_default("asset_received_but_not_billed")

		if self.update_stock:
			self.validate_item_code()
			self.validate_warehouse(for_validate)
			if auto_accounting_for_stock:
				warehouse_account = get_warehouse_account_map(self.company)

		for item in self.get("items"):
			# in case of auto inventory accounting,
			# expense account is always "Stock Received But Not Billed" for a stock item
			# except opening entry, drop-ship entry and fixed asset items
			if item.item_code:
				asset_category = frappe.get_cached_value("Item", item.item_code, "asset_category")

			if auto_accounting_for_stock and item.item_code in stock_items \
				and self.is_opening == 'No' and not item.is_fixed_asset \
				and (not item.po_detail or
					not frappe.db.get_value("Purchase Order Item", item.po_detail, "delivered_by_supplier")):

				if self.update_stock and (not item.from_warehouse):
					if for_validate and item.expense_account and item.expense_account != warehouse_account[item.warehouse]["account"]:
						msg = _("Row {}: Expense Head changed to {} ").format(item.idx, frappe.bold(warehouse_account[item.warehouse]["account"]))
						msg += _("because account {} is not linked to warehouse {} ").format(frappe.bold(item.expense_account), frappe.bold(item.warehouse))
						msg += _("or it is not the default inventory account")
						frappe.msgprint(msg, title=_("Expense Head Changed"))

					item.expense_account = warehouse_account[item.warehouse]["account"]
				else:
					# check if 'Stock Received But Not Billed' account is credited in Purchase receipt or not
					if item.purchase_receipt:
						negative_expense_booked_in_pr = frappe.db.sql("""select name from `tabGL Entry`
							where voucher_type='Purchase Receipt' and voucher_no=%s and account = %s""",
							(item.purchase_receipt, stock_not_billed_account))

						if negative_expense_booked_in_pr:
							if for_validate and item.expense_account and item.expense_account != stock_not_billed_account:
								msg = _("Row {}: Expense Head changed to {} ").format(item.idx, frappe.bold(stock_not_billed_account))
								msg += _("because expense is booked against this account in Purchase Receipt {}").format(frappe.bold(item.purchase_receipt))
								frappe.msgprint(msg, title=_("Expense Head Changed"))

							item.expense_account = stock_not_billed_account
					else:
						# If no purchase receipt present then book expense in 'Stock Received But Not Billed'
						# This is done in cases when Purchase Invoice is created before Purchase Receipt
						if for_validate and item.expense_account and item.expense_account != stock_not_billed_account:
							msg = _("Row {}: Expense Head changed to {} ").format(item.idx, frappe.bold(stock_not_billed_account))
							msg += _("as no Purchase Receipt is created against Item {}. ").format(frappe.bold(item.item_code))
							msg += _("This is done to handle accounting for cases when Purchase Receipt is created after Purchase Invoice")
							frappe.msgprint(msg, title=_("Expense Head Changed"))

						item.expense_account = stock_not_billed_account

			elif item.is_fixed_asset and not is_cwip_accounting_enabled(asset_category):
				item.expense_account = get_asset_category_account('fixed_asset_account', item=item.item_code,
					company = self.company)
			elif item.is_fixed_asset and item.pr_detail:
				item.expense_account = asset_received_but_not_billed
			elif not item.expense_account and for_validate:
				throw(_("Expense account is mandatory for item {0}").format(item.item_code or item.item_name))

	def set_against_expense_account(self):
		against_accounts = []
		for item in self.get("items"):
			if item.expense_account and (item.expense_account not in against_accounts):
				against_accounts.append(item.expense_account)

		self.against_expense_account = ",".join(against_accounts)

	def po_required(self):
		if frappe.db.get_value("Buying Settings", None, "po_required") == 'Yes':

			if frappe.get_value('Supplier', self.supplier, 'allow_purchase_invoice_creation_without_purchase_order'):
				return

			for d in self.get('items'):
				if not d.purchase_order:
					msg = _("Purchase Order Required for item {}").format(frappe.bold(d.item_code))
					msg += "<br><br>"
					msg += _("To submit the invoice without purchase order please set {} ").format(frappe.bold(_('Purchase Order Required')))
					msg += _("as {} in {}").format(frappe.bold('No'), get_link_to_form('Buying Settings', 'Buying Settings', 'Buying Settings'))
					throw(msg, title=_("Mandatory Purchase Order"))

	def pr_required(self):
		stock_items = self.get_stock_items()
		if frappe.db.get_value("Buying Settings", None, "pr_required") == 'Yes':

			if frappe.get_value('Supplier', self.supplier, 'allow_purchase_invoice_creation_without_purchase_receipt'):
				return

			for d in self.get('items'):
				if not d.purchase_receipt and d.item_code in stock_items:
					msg = _("Purchase Receipt Required for item {}").format(frappe.bold(d.item_code))
					msg += "<br><br>"
					msg += _("To submit the invoice without purchase receipt please set {} ").format(frappe.bold(_('Purchase Receipt Required')))
					msg += _("as {} in {}").format(frappe.bold('No'), get_link_to_form('Buying Settings', 'Buying Settings', 'Buying Settings'))
					throw(msg, title=_("Mandatory Purchase Receipt"))

	def validate_write_off_account(self):
		if self.write_off_amount and not self.write_off_account:
			throw(_("Please enter Write Off Account"))

	def check_prev_docstatus(self):
		for d in self.get('items'):
			if d.purchase_order:
				submitted = frappe.db.sql("select name from `tabPurchase Order` where docstatus = 1 and name = %s", d.purchase_order)
				if not submitted:
					frappe.throw(_("Purchase Order {0} is not submitted").format(d.purchase_order))
			if d.purchase_receipt:
				submitted = frappe.db.sql("select name from `tabPurchase Receipt` where docstatus = 1 and name = %s", d.purchase_receipt)
				if not submitted:
					frappe.throw(_("Purchase Receipt {0} is not submitted").format(d.purchase_receipt))

	def update_status_updater_args(self):
		if cint(self.update_stock):
			self.status_updater.append({
				'source_dt': 'Purchase Invoice Item',
				'target_dt': 'Purchase Order Item',
				'join_field': 'po_detail',
				'target_field': 'received_qty',
				'target_parent_dt': 'Purchase Order',
				'target_parent_field': 'per_received',
				'target_ref_field': 'qty',
				'source_field': 'received_qty',
				'second_source_dt': 'Purchase Receipt Item',
				'second_source_field': 'received_qty',
				'second_join_field': 'purchase_order_item',
				'percent_join_field':'purchase_order',
				'overflow_type': 'receipt',
				'extra_cond': """ and exists(select name from `tabPurchase Invoice`
					where name=`tabPurchase Invoice Item`.parent and update_stock = 1)"""
			})
			if cint(self.is_return):
				self.status_updater.append({
					'source_dt': 'Purchase Invoice Item',
					'target_dt': 'Purchase Order Item',
					'join_field': 'po_detail',
					'target_field': 'returned_qty',
					'source_field': '-1 * qty',
					'second_source_dt': 'Purchase Receipt Item',
					'second_source_field': '-1 * qty',
					'second_join_field': 'purchase_order_item',
					'overflow_type': 'receipt',
					'extra_cond': """ and exists (select name from `tabPurchase Invoice`
						where name=`tabPurchase Invoice Item`.parent and update_stock=1 and is_return=1)"""
				})

	def validate_purchase_receipt_if_update_stock(self):
		if self.update_stock:
			for item in self.get("items"):
				if item.purchase_receipt:
					frappe.throw(_("Stock cannot be updated against Purchase Receipt {0}")
						.format(item.purchase_receipt))

	def on_submit(self):
		super(PurchaseInvoice, self).on_submit()

		self.check_prev_docstatus()
		self.update_status_updater_args()
		self.update_prevdoc_status()

		frappe.get_doc('Authorization Control').validate_approving_authority(self.doctype,
			self.company, self.base_grand_total)

		if not self.is_return:
			self.update_against_document_in_jv()
			self.update_billing_status_for_zero_amount_refdoc("Purchase Receipt")
			self.update_billing_status_for_zero_amount_refdoc("Purchase Order")

		self.update_billing_status_in_pr()

		# Updating stock ledger should always be called after updating prevdoc status,
		# because updating ordered qty in bin depends upon updated ordered qty in PO
		if self.update_stock == 1:
			self.update_stock_ledger()
			from erpnext.stock.doctype.serial_no.serial_no import update_serial_nos_after_submit
			update_serial_nos_after_submit(self, "items")

		# this sequence because outstanding may get -negative
		self.make_gl_entries()

		if self.update_stock == 1:
			self.repost_future_sle_and_gle()

		self.update_project()
		update_linked_doc(self.doctype, self.name, self.inter_company_invoice_reference)

	def make_gl_entries(self, gl_entries=None, from_repost=False):
		if not gl_entries:
			gl_entries = self.get_gl_entries()

		if gl_entries:
			update_outstanding = "No" if (cint(self.is_paid) or self.write_off_account) else "Yes"

			if self.docstatus == 1:
				make_gl_entries(gl_entries, update_outstanding=update_outstanding, merge_entries=False, from_repost=from_repost)
			elif self.docstatus == 2:
				make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)

			if update_outstanding == "No":
				update_outstanding_amt(self.credit_to, "Supplier", self.supplier,
					self.doctype, self.return_against if cint(self.is_return) and self.return_against else self.name)

		elif self.docstatus == 2 and cint(self.update_stock) and self.auto_accounting_for_stock:
			make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)

	def get_gl_entries(self, warehouse_account=None):
		self.auto_accounting_for_stock = erpnext.is_perpetual_inventory_enabled(self.company)
		if self.auto_accounting_for_stock:
			self.stock_received_but_not_billed = self.get_company_default("stock_received_but_not_billed")
			self.expenses_included_in_valuation = self.get_company_default("expenses_included_in_valuation")
		else:
			self.stock_received_but_not_billed = None
			self.expenses_included_in_valuation = None

		self.negative_expense_to_be_booked = 0.0
		gl_entries = []

		self.make_supplier_gl_entry(gl_entries)
		self.make_item_gl_entries(gl_entries)

		if self.check_asset_cwip_enabled():
			self.get_asset_gl_entry(gl_entries)

		self.make_tax_gl_entries(gl_entries)
		self.make_internal_transfer_gl_entries(gl_entries)

		gl_entries = make_regional_gl_entries(gl_entries, self)

		gl_entries = merge_similar_entries(gl_entries)

		self.make_payment_gl_entries(gl_entries)
		self.make_write_off_gl_entry(gl_entries)
		self.make_gle_for_rounding_adjustment(gl_entries)
		return gl_entries

	def check_asset_cwip_enabled(self):
		# Check if there exists any item with cwip accounting enabled in it's asset category
		for item in self.get("items"):
			if item.item_code and item.is_fixed_asset:
				asset_category = frappe.get_cached_value("Item", item.item_code, "asset_category")
				if is_cwip_accounting_enabled(asset_category):
					return 1
		return 0

	def make_supplier_gl_entry(self, gl_entries):
		# Checked both rounding_adjustment and rounded_total
		# because rounded_total had value even before introcution of posting GLE based on rounded total
		grand_total = self.rounded_total if (self.rounding_adjustment and self.rounded_total) else self.grand_total

		if grand_total and not self.is_internal_transfer():
				# Did not use base_grand_total to book rounding loss gle
				grand_total_in_company_currency = flt(grand_total * self.conversion_rate,
					self.precision("grand_total"))
				gl_entries.append(
					self.get_gl_dict({
						"account": self.credit_to,
						"party_type": "Supplier",
						"party": self.supplier,
						"due_date": self.due_date,
						"against": self.against_expense_account,
						"credit": grand_total_in_company_currency,
						"credit_in_account_currency": grand_total_in_company_currency \
							if self.party_account_currency==self.company_currency else grand_total,
						"against_voucher": self.return_against if cint(self.is_return) and self.return_against else self.name,
						"against_voucher_type": self.doctype,
						"project": self.project,
						"cost_center": self.cost_center
					}, self.party_account_currency, item=self)
				)

	def make_item_gl_entries(self, gl_entries):
		# item gl entries
		stock_items = self.get_stock_items()
		if self.update_stock and self.auto_accounting_for_stock:
			warehouse_account = get_warehouse_account_map(self.company)

		landed_cost_entries = get_item_account_wise_additional_cost(self.name)

		voucher_wise_stock_value = {}
		if self.update_stock:
			for d in frappe.get_all('Stock Ledger Entry',
				fields = ["voucher_detail_no", "stock_value_difference", "warehouse"], filters={'voucher_no': self.name}):
				voucher_wise_stock_value.setdefault((d.voucher_detail_no, d.warehouse), d.stock_value_difference)

		valuation_tax_accounts = [d.account_head for d in self.get("taxes")
			if d.category in ('Valuation', 'Total and Valuation')
			and flt(d.base_tax_amount_after_discount_amount)]

		for item in self.get("items"):
			if flt(item.base_net_amount):
				account_currency = get_account_currency(item.expense_account)
				if item.item_code:
					asset_category = frappe.get_cached_value("Item", item.item_code, "asset_category")

				if self.update_stock and self.auto_accounting_for_stock and item.item_code in stock_items:
					# warehouse account
					warehouse_debit_amount = self.make_stock_adjustment_entry(gl_entries,
						item, voucher_wise_stock_value, account_currency)

					if item.from_warehouse:
						gl_entries.append(self.get_gl_dict({
							"account":  warehouse_account[item.warehouse]['account'],
							"against": warehouse_account[item.from_warehouse]["account"],
							"cost_center": item.cost_center,
							"project": item.project or self.project,
							"remarks": self.get("remarks") or _("Accounting Entry for Stock"),
							"debit": warehouse_debit_amount,
						}, warehouse_account[item.warehouse]["account_currency"], item=item))

						# Intentionally passed negative debit amount to avoid incorrect GL Entry validation
						gl_entries.append(self.get_gl_dict({
							"account":  warehouse_account[item.from_warehouse]['account'],
							"against": warehouse_account[item.warehouse]["account"],
							"cost_center": item.cost_center,
							"project": item.project or self.project,
							"remarks": self.get("remarks") or _("Accounting Entry for Stock"),
							"debit": -1 * flt(item.base_net_amount, item.precision("base_net_amount")),
						}, warehouse_account[item.from_warehouse]["account_currency"], item=item))

						# Do not book expense for transfer within same company transfer
						if not self.is_internal_transfer():
							gl_entries.append(
								self.get_gl_dict({
									"account": item.expense_account,
									"against": self.supplier,
									"debit": flt(item.base_net_amount, item.precision("base_net_amount")),
									"remarks": self.get("remarks") or _("Accounting Entry for Stock"),
									"cost_center": item.cost_center,
									"project": item.project
								}, account_currency, item=item)
							)

					else:
						if not self.is_internal_transfer():
							gl_entries.append(
								self.get_gl_dict({
									"account": item.expense_account,
									"against": self.supplier,
									"debit": warehouse_debit_amount,
									"remarks": self.get("remarks") or _("Accounting Entry for Stock"),
									"cost_center": item.cost_center,
									"project": item.project or self.project
								}, account_currency, item=item)
							)

					# Amount added through landed-cost-voucher
					if landed_cost_entries:
						for account, amount in iteritems(landed_cost_entries[(item.item_code, item.name)]):
							gl_entries.append(self.get_gl_dict({
								"account": account,
								"against": item.expense_account,
								"cost_center": item.cost_center,
								"remarks": self.get("remarks") or _("Accounting Entry for Stock"),
								"credit": flt(amount["base_amount"]),
								"credit_in_account_currency": flt(amount["amount"]),
								"project": item.project or self.project
							}, item=item))

					# sub-contracting warehouse
					if flt(item.rm_supp_cost):
						supplier_warehouse_account = warehouse_account[self.supplier_warehouse]["account"]
						if not supplier_warehouse_account:
							frappe.throw(_("Please set account in Warehouse {0}")
								.format(self.supplier_warehouse))
						gl_entries.append(self.get_gl_dict({
							"account": supplier_warehouse_account,
							"against": item.expense_account,
							"cost_center": item.cost_center,
							"project": item.project or self.project,
							"remarks": self.get("remarks") or _("Accounting Entry for Stock"),
							"credit": flt(item.rm_supp_cost)
						}, warehouse_account[self.supplier_warehouse]["account_currency"], item=item))

				elif not item.is_fixed_asset or (item.is_fixed_asset and not is_cwip_accounting_enabled(asset_category)):
					expense_account = (item.expense_account
						if (not item.enable_deferred_expense or self.is_return) else item.deferred_expense_account)

					if not item.is_fixed_asset:
						amount = flt(item.base_net_amount, item.precision("base_net_amount"))
					else:
						amount = flt(item.base_net_amount + item.item_tax_amount, item.precision("base_net_amount"))

					auto_accounting_for_non_stock_items = cint(frappe.db.get_value('Company', self.company, 'enable_perpetual_inventory_for_non_stock_items'))

					if auto_accounting_for_non_stock_items:
						service_received_but_not_billed_account = self.get_company_default("service_received_but_not_billed")

						if item.purchase_receipt:
							# Post reverse entry for Stock-Received-But-Not-Billed if it is booked in Purchase Receipt
							expense_booked_in_pr = frappe.db.get_value('GL Entry', {'is_cancelled': 0,
								'voucher_type': 'Purchase Receipt', 'voucher_no': item.purchase_receipt, 'voucher_detail_no': item.pr_detail,
								'account':service_received_but_not_billed_account}, ['name'])

							if expense_booked_in_pr:
								expense_account = service_received_but_not_billed_account

					if not self.is_internal_transfer():
						gl_entries.append(self.get_gl_dict({
								"account": expense_account,
								"against": self.supplier,
								"debit": amount,
								"cost_center": item.cost_center,
								"project": item.project or self.project
							}, account_currency, item=item))

					# If asset is bought through this document and not linked to PR
					if self.update_stock and item.landed_cost_voucher_amount:
						expenses_included_in_asset_valuation = self.get_company_default("expenses_included_in_asset_valuation")
						# Amount added through landed-cost-voucher
						gl_entries.append(self.get_gl_dict({
							"account": expenses_included_in_asset_valuation,
							"against": expense_account,
							"cost_center": item.cost_center,
							"remarks": self.get("remarks") or _("Accounting Entry for Stock"),
							"credit": flt(item.landed_cost_voucher_amount),
							"project": item.project or self.project
						}, item=item))

						gl_entries.append(self.get_gl_dict({
							"account": expense_account,
							"against": expenses_included_in_asset_valuation,
							"cost_center": item.cost_center,
							"remarks": self.get("remarks") or _("Accounting Entry for Stock"),
							"debit": flt(item.landed_cost_voucher_amount),
							"project": item.project or self.project
						}, item=item))

						# update gross amount of asset bought through this document
						assets = frappe.db.get_all('Asset',
							filters={ 'purchase_invoice': self.name, 'item_code': item.item_code }
						)
						for asset in assets:
							frappe.db.set_value("Asset", asset.name, "gross_purchase_amount", flt(item.valuation_rate))
							frappe.db.set_value("Asset", asset.name, "purchase_receipt_amount", flt(item.valuation_rate))

			if self.auto_accounting_for_stock and self.is_opening == "No" and \
				item.item_code in stock_items and item.item_tax_amount:
					# Post reverse entry for Stock-Received-But-Not-Billed if it is booked in Purchase Receipt
					if item.purchase_receipt and valuation_tax_accounts:
						negative_expense_booked_in_pr = frappe.db.sql("""select name from `tabGL Entry`
							where voucher_type='Purchase Receipt' and voucher_no=%s and account in %s""",
							(item.purchase_receipt, valuation_tax_accounts))

						if not negative_expense_booked_in_pr:
							gl_entries.append(
								self.get_gl_dict({
									"account": self.stock_received_but_not_billed,
									"against": self.supplier,
									"debit": flt(item.item_tax_amount, item.precision("item_tax_amount")),
									"remarks": self.remarks or "Accounting Entry for Stock",
									"cost_center": self.cost_center,
									"project": item.project or self.project
								}, item=item)
							)

							self.negative_expense_to_be_booked += flt(item.item_tax_amount, \
								item.precision("item_tax_amount"))

	def get_asset_gl_entry(self, gl_entries):
		arbnb_account = self.get_company_default("asset_received_but_not_billed")
		eiiav_account = self.get_company_default("expenses_included_in_asset_valuation")

		for item in self.get("items"):
			if item.is_fixed_asset:
				asset_amount = flt(item.net_amount) + flt(item.item_tax_amount/self.conversion_rate)
				base_asset_amount = flt(item.base_net_amount + item.item_tax_amount)

				item_exp_acc_type = frappe.db.get_value('Account', item.expense_account, 'account_type')
				if (not item.expense_account or item_exp_acc_type not in ['Asset Received But Not Billed', 'Fixed Asset']):
					item.expense_account = arbnb_account

				if not self.update_stock:
					arbnb_currency = get_account_currency(item.expense_account)
					gl_entries.append(self.get_gl_dict({
						"account": item.expense_account,
						"against": self.supplier,
						"remarks": self.get("remarks") or _("Accounting Entry for Asset"),
						"debit": base_asset_amount,
						"debit_in_account_currency": (base_asset_amount
							if arbnb_currency == self.company_currency else asset_amount),
						"cost_center": item.cost_center,
						"project": item.project or self.project
					}, item=item))

					if item.item_tax_amount:
						asset_eiiav_currency = get_account_currency(eiiav_account)
						gl_entries.append(self.get_gl_dict({
							"account": eiiav_account,
							"against": self.supplier,
							"remarks": self.get("remarks") or _("Accounting Entry for Asset"),
							"cost_center": item.cost_center,
							"project": item.project or self.project,
							"credit": item.item_tax_amount,
							"credit_in_account_currency": (item.item_tax_amount
								if asset_eiiav_currency == self.company_currency else
									item.item_tax_amount / self.conversion_rate)
						}, item=item))
				else:
					cwip_account = get_asset_account("capital_work_in_progress_account",
						asset_category=item.asset_category,company=self.company)

					cwip_account_currency = get_account_currency(cwip_account)
					gl_entries.append(self.get_gl_dict({
						"account": cwip_account,
						"against": self.supplier,
						"remarks": self.get("remarks") or _("Accounting Entry for Asset"),
						"debit": base_asset_amount,
						"debit_in_account_currency": (base_asset_amount
							if cwip_account_currency == self.company_currency else asset_amount),
						"cost_center": self.cost_center,
						"project": item.project or self.project
					}, item=item))

					if item.item_tax_amount and not cint(erpnext.is_perpetual_inventory_enabled(self.company)):
						asset_eiiav_currency = get_account_currency(eiiav_account)
						gl_entries.append(self.get_gl_dict({
							"account": eiiav_account,
							"against": self.supplier,
							"remarks": self.get("remarks") or _("Accounting Entry for Asset"),
							"cost_center": item.cost_center,
							"credit": item.item_tax_amount,
							"project": item.project or self.project,
							"credit_in_account_currency": (item.item_tax_amount
								if asset_eiiav_currency == self.company_currency else
									item.item_tax_amount / self.conversion_rate)
						}, item=item))

					# When update stock is checked
					# Assets are bought through this document then it will be linked to this document
					if self.update_stock:
						if flt(item.landed_cost_voucher_amount):
							gl_entries.append(self.get_gl_dict({
								"account": eiiav_account,
								"against": cwip_account,
								"cost_center": item.cost_center,
								"remarks": self.get("remarks") or _("Accounting Entry for Stock"),
								"credit": flt(item.landed_cost_voucher_amount),
								"project": item.project or self.project
							}, item=item))

							gl_entries.append(self.get_gl_dict({
								"account": cwip_account,
								"against": eiiav_account,
								"cost_center": item.cost_center,
								"remarks": self.get("remarks") or _("Accounting Entry for Stock"),
								"debit": flt(item.landed_cost_voucher_amount),
								"project": item.project or self.project
							}, item=item))

						# update gross amount of assets bought through this document
						assets = frappe.db.get_all('Asset',
							filters={ 'purchase_invoice': self.name, 'item_code': item.item_code }
						)
						for asset in assets:
							frappe.db.set_value("Asset", asset.name, "gross_purchase_amount", flt(item.valuation_rate))
							frappe.db.set_value("Asset", asset.name, "purchase_receipt_amount", flt(item.valuation_rate))

		return gl_entries

	def make_stock_adjustment_entry(self, gl_entries, item, voucher_wise_stock_value, account_currency):
		net_amt_precision = item.precision("base_net_amount")
		val_rate_db_precision = 6 if cint(item.precision("valuation_rate")) <= 6 else 9

		warehouse_debit_amount = flt(flt(item.valuation_rate, val_rate_db_precision)
			* flt(item.qty)	* flt(item.conversion_factor), net_amt_precision)

		# Stock ledger value is not matching with the warehouse amount
		if (self.update_stock and voucher_wise_stock_value.get(item.name) and
			warehouse_debit_amount != flt(voucher_wise_stock_value.get((item.name, item.warehouse)), net_amt_precision)):

			cost_of_goods_sold_account = self.get_company_default("default_expense_account")
			stock_amount = flt(voucher_wise_stock_value.get((item.name, item.warehouse)), net_amt_precision)
			stock_adjustment_amt = warehouse_debit_amount - stock_amount

			gl_entries.append(
				self.get_gl_dict({
					"account": cost_of_goods_sold_account,
					"against": item.expense_account,
					"debit": stock_adjustment_amt,
					"remarks": self.get("remarks") or _("Stock Adjustment"),
					"cost_center": item.cost_center,
					"project": item.project or self.project
				}, account_currency, item=item)
			)

			warehouse_debit_amount = stock_amount

		return warehouse_debit_amount

	def make_tax_gl_entries(self, gl_entries):
		# tax table gl entries
		valuation_tax = {}
		for tax in self.get("taxes"):
			if tax.category in ("Total", "Valuation and Total") and flt(tax.base_tax_amount_after_discount_amount):
				account_currency = get_account_currency(tax.account_head)

				dr_or_cr = "debit" if tax.add_deduct_tax == "Add" else "credit"

				gl_entries.append(
					self.get_gl_dict({
						"account": tax.account_head,
						"against": self.supplier,
						dr_or_cr: tax.base_tax_amount_after_discount_amount,
						dr_or_cr + "_in_account_currency": tax.base_tax_amount_after_discount_amount \
							if account_currency==self.company_currency \
							else tax.tax_amount_after_discount_amount,
						"cost_center": tax.cost_center
					}, account_currency, item=tax)
				)
			# accumulate valuation tax
			if self.is_opening == "No" and tax.category in ("Valuation", "Valuation and Total") and flt(tax.base_tax_amount_after_discount_amount) \
				and not self.is_internal_transfer():
				if self.auto_accounting_for_stock and not tax.cost_center:
					frappe.throw(_("Cost Center is required in row {0} in Taxes table for type {1}").format(tax.idx, _(tax.category)))
				valuation_tax.setdefault(tax.name, 0)
				valuation_tax[tax.name] += \
					(tax.add_deduct_tax == "Add" and 1 or -1) * flt(tax.base_tax_amount_after_discount_amount)

		if self.is_opening == "No" and self.negative_expense_to_be_booked and valuation_tax:
			# credit valuation tax amount in "Expenses Included In Valuation"
			# this will balance out valuation amount included in cost of goods sold

			total_valuation_amount = sum(valuation_tax.values())
			amount_including_divisional_loss = self.negative_expense_to_be_booked
			i = 1
			for tax in self.get("taxes"):
				if valuation_tax.get(tax.name):
					if i == len(valuation_tax):
						applicable_amount = amount_including_divisional_loss
					else:
						applicable_amount = self.negative_expense_to_be_booked * (valuation_tax[tax.name] / total_valuation_amount)
						amount_including_divisional_loss -= applicable_amount

					gl_entries.append(
						self.get_gl_dict({
							"account": tax.account_head,
							"cost_center": tax.cost_center,
							"against": self.supplier,
							"credit": applicable_amount,
							"remarks": self.remarks or _("Accounting Entry for Stock"),
						}, item=tax)
					)

					i += 1

		if self.auto_accounting_for_stock and self.update_stock and valuation_tax:
			for tax in self.get("taxes"):
				if valuation_tax.get(tax.name):
					gl_entries.append(
						self.get_gl_dict({
							"account": tax.account_head,
							"cost_center": tax.cost_center,
							"against": self.supplier,
							"credit": valuation_tax[tax.name],
							"remarks": self.remarks or "Accounting Entry for Stock"
						}, item=tax))

	def make_internal_transfer_gl_entries(self, gl_entries):
		if self.is_internal_transfer() and flt(self.base_total_taxes_and_charges):
			account_currency = get_account_currency(self.unrealized_profit_loss_account)
			gl_entries.append(
				self.get_gl_dict({
					"account": self.unrealized_profit_loss_account,
					"against": self.supplier,
					"credit": flt(self.total_taxes_and_charges),
					"credit_in_account_currency": flt(self.base_total_taxes_and_charges),
					"cost_center": self.cost_center
				}, account_currency, item=self))

	def make_payment_gl_entries(self, gl_entries):
		# Make Cash GL Entries
		if cint(self.is_paid) and self.cash_bank_account and self.paid_amount:
			bank_account_currency = get_account_currency(self.cash_bank_account)
			# CASH, make payment entries
			gl_entries.append(
				self.get_gl_dict({
					"account": self.credit_to,
					"party_type": "Supplier",
					"party": self.supplier,
					"against": self.cash_bank_account,
					"debit": self.base_paid_amount,
					"debit_in_account_currency": self.base_paid_amount \
						if self.party_account_currency==self.company_currency else self.paid_amount,
					"against_voucher": self.return_against if cint(self.is_return) and self.return_against else self.name,
					"against_voucher_type": self.doctype,
					"cost_center": self.cost_center,
					"project": self.project
				}, self.party_account_currency, item=self)
			)

			gl_entries.append(
				self.get_gl_dict({
					"account": self.cash_bank_account,
					"against": self.supplier,
					"credit": self.base_paid_amount,
					"credit_in_account_currency": self.base_paid_amount \
						if bank_account_currency==self.company_currency else self.paid_amount,
					"cost_center": self.cost_center
				}, bank_account_currency, item=self)
			)

	def make_write_off_gl_entry(self, gl_entries):
		# writeoff account includes petty difference in the invoice amount
		# and the amount that is paid
		if self.write_off_account and flt(self.write_off_amount):
			write_off_account_currency = get_account_currency(self.write_off_account)

			gl_entries.append(
				self.get_gl_dict({
					"account": self.credit_to,
					"party_type": "Supplier",
					"party": self.supplier,
					"against": self.write_off_account,
					"debit": self.base_write_off_amount,
					"debit_in_account_currency": self.base_write_off_amount \
						if self.party_account_currency==self.company_currency else self.write_off_amount,
					"against_voucher": self.return_against if cint(self.is_return) and self.return_against else self.name,
					"against_voucher_type": self.doctype,
					"cost_center": self.cost_center,
					"project": self.project
				}, self.party_account_currency, item=self)
			)
			gl_entries.append(
				self.get_gl_dict({
					"account": self.write_off_account,
					"against": self.supplier,
					"credit": flt(self.base_write_off_amount),
					"credit_in_account_currency": self.base_write_off_amount \
						if write_off_account_currency==self.company_currency else self.write_off_amount,
					"cost_center": self.cost_center or self.write_off_cost_center
				}, item=self)
			)

	def make_gle_for_rounding_adjustment(self, gl_entries):
		# if rounding adjustment in small and conversion rate is also small then
		# base_rounding_adjustment may become zero due to small precision
		# eg: rounding_adjustment = 0.01 and exchange rate = 0.05 and precision of base_rounding_adjustment is 2
		#	then base_rounding_adjustment becomes zero and error is thrown in GL Entry
		if self.rounding_adjustment and self.base_rounding_adjustment:
			round_off_account, round_off_cost_center = \
				get_round_off_account_and_cost_center(self.company)

			gl_entries.append(
				self.get_gl_dict({
					"account": round_off_account,
					"against": self.supplier,
					"debit_in_account_currency": self.rounding_adjustment,
					"debit": self.base_rounding_adjustment,
					"cost_center": self.cost_center or round_off_cost_center,
				}, item=self))

	def on_cancel(self):
		super(PurchaseInvoice, self).on_cancel()

		self.check_on_hold_or_closed_status()

		self.update_status_updater_args()
		self.update_prevdoc_status()

		if not self.is_return:
			self.update_billing_status_for_zero_amount_refdoc("Purchase Receipt")
			self.update_billing_status_for_zero_amount_refdoc("Purchase Order")

		self.update_billing_status_in_pr()

		# Updating stock ledger should always be called after updating prevdoc status,
		# because updating ordered qty in bin depends upon updated ordered qty in PO
		if self.update_stock == 1:
			self.update_stock_ledger()
			self.delete_auto_created_batches()

		self.make_gl_entries_on_cancel()

		if self.update_stock == 1:
			self.repost_future_sle_and_gle()

		self.update_project()
		frappe.db.set(self, 'status', 'Cancelled')

		unlink_inter_company_doc(self.doctype, self.name, self.inter_company_invoice_reference)
		self.ignore_linked_doctypes = ('GL Entry', 'Stock Ledger Entry', 'Repost Item Valuation')

	def update_project(self):
		project_list = []
		for d in self.items:
			if d.project and d.project not in project_list:
				project = frappe.get_doc("Project", d.project)
				project.update_purchase_costing()
				project.db_update()
				project_list.append(d.project)

	def validate_supplier_invoice(self):
		if self.bill_date:
			if getdate(self.bill_date) > getdate(self.posting_date):
				frappe.throw(_("Supplier Invoice Date cannot be greater than Posting Date"))

		if self.bill_no:
			if cint(frappe.db.get_single_value("Accounts Settings", "check_supplier_invoice_uniqueness")):
				fiscal_year = get_fiscal_year(self.posting_date, company=self.company, as_dict=True)

				pi = frappe.db.sql('''select name from `tabPurchase Invoice`
					where
						bill_no = %(bill_no)s
						and supplier = %(supplier)s
						and name != %(name)s
						and docstatus < 2
						and posting_date between %(year_start_date)s and %(year_end_date)s''', {
							"bill_no": self.bill_no,
							"supplier": self.supplier,
							"name": self.name,
							"year_start_date": fiscal_year.year_start_date,
							"year_end_date": fiscal_year.year_end_date
						})

				if pi:
					pi = pi[0][0]
					frappe.throw(_("Supplier Invoice No exists in Purchase Invoice {0}").format(pi))

	def update_billing_status_in_pr(self, update_modified=True):
		updated_pr = []
		for d in self.get("items"):
			if d.pr_detail:
				billed_amt = frappe.db.sql("""select sum(amount) from `tabPurchase Invoice Item`
					where pr_detail=%s and docstatus=1""", d.pr_detail)
				billed_amt = billed_amt and billed_amt[0][0] or 0
				frappe.db.set_value("Purchase Receipt Item", d.pr_detail, "billed_amt", billed_amt, update_modified=update_modified)
				updated_pr.append(d.purchase_receipt)
			elif d.po_detail:
				updated_pr += update_billed_amount_based_on_po(d.po_detail, update_modified)

		for pr in set(updated_pr):
			from erpnext.stock.doctype.purchase_receipt.purchase_receipt import update_billing_percentage
			pr_doc = frappe.get_doc("Purchase Receipt", pr)
			update_billing_percentage(pr_doc, update_modified=update_modified)

	def on_recurring(self, reference_doc, auto_repeat_doc):
		self.due_date = None

	def block_invoice(self, hold_comment=None, release_date=None):
		self.db_set('on_hold', 1)
		self.db_set('hold_comment', cstr(hold_comment))
		self.db_set('release_date', release_date)

	def unblock_invoice(self):
		self.db_set('on_hold', 0)
		self.db_set('release_date', None)

	def set_tax_withholding(self):
		if not self.apply_tds:
			return

		tax_withholding_details = get_party_tax_withholding_details(self, self.tax_withholding_category)

		if not tax_withholding_details:
			return

		accounts = []
		for d in self.taxes:
			if d.account_head == tax_withholding_details.get("account_head"):
				d.update(tax_withholding_details)
			accounts.append(d.account_head)

		if not accounts or tax_withholding_details.get("account_head") not in accounts:
			self.append("taxes", tax_withholding_details)

		to_remove = [d for d in self.taxes
			if not d.tax_amount and d.account_head == tax_withholding_details.get("account_head")]

		for d in to_remove:
			self.remove(d)

		# calculate totals again after applying TDS
		self.calculate_taxes_and_totals()

	def set_status(self, update=False, status=None, update_modified=True):
		if self.is_new():
			if self.get('amended_from'):
				self.status = 'Draft'
			return

		precision = self.precision("outstanding_amount")
		outstanding_amount = flt(self.outstanding_amount, precision)
		due_date = getdate(self.due_date)
		nowdate = getdate()

		if not status:
			if self.docstatus == 2:
				status = "Cancelled"
			elif self.docstatus == 1:
				if self.is_internal_transfer():
					self.status = 'Internal Transfer'
				elif outstanding_amount > 0 and due_date < nowdate:
					self.status = "Overdue"
				elif outstanding_amount > 0 and due_date >= nowdate:
					self.status = "Unpaid"
				#Check if outstanding amount is 0 due to debit note issued against invoice
				elif outstanding_amount <= 0 and self.is_return == 0 and frappe.db.get_value('Purchase Invoice', {'is_return': 1, 'return_against': self.name, 'docstatus': 1}):
					self.status = "Debit Note Issued"
				elif self.is_return == 1:
					self.status = "Return"
				elif outstanding_amount<=0:
					self.status = "Paid"
				else:
					self.status = "Submitted"
			else:
				self.status = "Draft"

		if update:
			self.db_set('status', self.status, update_modified = update_modified)

def get_list_context(context=None):
	from erpnext.controllers.website_list_for_contact import get_list_context
	list_context = get_list_context(context)
	list_context.update({
		'show_sidebar': True,
		'show_search': True,
		'no_breadcrumbs': True,
		'title': _('Purchase Invoices'),
	})
	return list_context

@erpnext.allow_regional
def make_regional_gl_entries(gl_entries, doc):
	return gl_entries

@frappe.whitelist()
def make_debit_note(source_name, target_doc=None):
	from erpnext.controllers.sales_and_purchase_return import make_return_doc
	return make_return_doc("Purchase Invoice", source_name, target_doc)

@frappe.whitelist()
def make_stock_entry(source_name, target_doc=None):
	doc = get_mapped_doc("Purchase Invoice", source_name, {
		"Purchase Invoice": {
			"doctype": "Stock Entry",
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Purchase Invoice Item": {
			"doctype": "Stock Entry Detail",
			"field_map": {
				"stock_qty": "transfer_qty",
				"batch_no": "batch_no"
			},
		}
	}, target_doc)

	return doc

@frappe.whitelist()
def change_release_date(name, release_date=None):
	if frappe.db.exists('Purchase Invoice', name):
		pi = frappe.get_doc('Purchase Invoice', name)
		pi.db_set('release_date', release_date)


@frappe.whitelist()
def unblock_invoice(name):
	if frappe.db.exists('Purchase Invoice', name):
		pi = frappe.get_doc('Purchase Invoice', name)
		pi.unblock_invoice()


@frappe.whitelist()
def block_invoice(name, release_date, hold_comment=None):
	if frappe.db.exists('Purchase Invoice', name):
		pi = frappe.get_doc('Purchase Invoice', name)
		pi.block_invoice(hold_comment, release_date)

@frappe.whitelist()
def make_inter_company_sales_invoice(source_name, target_doc=None):
	from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_inter_company_transaction
	return make_inter_company_transaction("Purchase Invoice", source_name, target_doc)

def on_doctype_update():
	frappe.db.add_index("Purchase Invoice", ["supplier", "is_return", "return_against"])
