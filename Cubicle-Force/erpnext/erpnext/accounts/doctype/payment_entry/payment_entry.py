# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, erpnext, json
from frappe import _, scrub, ValidationError
from frappe.utils import flt, comma_or, nowdate, getdate
from erpnext.accounts.utils import get_outstanding_invoices, get_account_currency, get_balance_on
from erpnext.accounts.party import get_party_account
from erpnext.accounts.doctype.journal_entry.journal_entry import get_default_bank_cash_account
from erpnext.setup.utils import get_exchange_rate
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.hr.doctype.expense_claim.expense_claim import update_reimbursed_amount
from erpnext.accounts.doctype.bank_account.bank_account import get_party_bank_account, get_bank_account_details
from erpnext.controllers.accounts_controller import AccountsController, get_supplier_block_status
from erpnext.accounts.doctype.invoice_discounting.invoice_discounting import get_party_account_based_on_invoice_discounting

from six import string_types, iteritems

class InvalidPaymentEntry(ValidationError):
	pass


class PaymentEntry(AccountsController):
	def __init__(self, *args, **kwargs):
		super(PaymentEntry, self).__init__(*args, **kwargs)
		if not self.is_new():
			self.setup_party_account_field()

	def setup_party_account_field(self):
		self.party_account_field = None
		self.party_account = None
		self.party_account_currency = None

		if self.payment_type == "Receive":
			self.party_account_field = "paid_from"
			self.party_account = self.paid_from
			self.party_account_currency = self.paid_from_account_currency

		elif self.payment_type == "Pay":
			self.party_account_field = "paid_to"
			self.party_account = self.paid_to
			self.party_account_currency = self.paid_to_account_currency

	def validate(self):
		self.setup_party_account_field()
		self.set_missing_values()
		self.validate_payment_type()
		self.validate_party_details()
		self.validate_bank_accounts()
		self.set_exchange_rate()
		self.validate_mandatory()
		self.validate_reference_documents()
		self.set_amounts()
		self.clear_unallocated_reference_document_rows()
		self.validate_payment_against_negative_invoice()
		self.validate_transaction_reference()
		self.set_title()
		self.set_remarks()
		self.validate_duplicate_entry()
		self.validate_allocated_amount()
		self.validate_paid_invoices()
		self.ensure_supplier_is_not_blocked()
		self.set_status()

	def on_submit(self):
		self.setup_party_account_field()
		if self.difference_amount:
			frappe.throw(_("Difference Amount must be zero"))
		self.make_gl_entries()
		self.update_outstanding_amounts()
		self.update_advance_paid()
		self.update_expense_claim()
		self.update_payment_schedule()
		self.set_status()

	def on_cancel(self):
		self.ignore_linked_doctypes = ('GL Entry', 'Stock Ledger Entry')
		self.setup_party_account_field()
		self.make_gl_entries(cancel=1)
		self.update_outstanding_amounts()
		self.update_advance_paid()
		self.update_expense_claim()
		self.delink_advance_entry_references()
		self.update_payment_schedule(cancel=1)
		self.set_payment_req_status()
		self.set_status()

	def set_payment_req_status(self):
		from erpnext.accounts.doctype.payment_request.payment_request import update_payment_req_status
		update_payment_req_status(self, None)

	def update_outstanding_amounts(self):
		self.set_missing_ref_details(force=True)

	def validate_duplicate_entry(self):
		reference_names = []
		for d in self.get("references"):
			if (d.reference_doctype, d.reference_name, d.payment_term) in reference_names:
				frappe.throw(_("Row #{0}: Duplicate entry in References {1} {2}")
					.format(d.idx, d.reference_doctype, d.reference_name))
			reference_names.append((d.reference_doctype, d.reference_name, d.payment_term))

	def set_bank_account_data(self):
		if self.bank_account:
			bank_data = get_bank_account_details(self.bank_account)

			field = "paid_from" if self.payment_type == "Pay" else "paid_to"

			self.bank = bank_data.bank
			self.bank_account_no = bank_data.bank_account_no

			if not self.get(field):
				self.set(field, bank_data.account)

	def validate_allocated_amount(self):
		for d in self.get("references"):
			if (flt(d.allocated_amount))> 0:
				if flt(d.allocated_amount) > flt(d.outstanding_amount):
					frappe.throw(_("Row #{0}: Allocated Amount cannot be greater than outstanding amount.").format(d.idx))

	def delink_advance_entry_references(self):
		for reference in self.references:
			if reference.reference_doctype in ("Sales Invoice", "Purchase Invoice"):
				doc = frappe.get_doc(reference.reference_doctype, reference.reference_name)
				doc.delink_advance_entries(self.name)

	def set_missing_values(self):
		if self.payment_type == "Internal Transfer":
			for field in ("party", "party_balance", "total_allocated_amount",
				"base_total_allocated_amount", "unallocated_amount"):
					self.set(field, None)
			self.references = []
		else:
			if not self.party_type:
				frappe.throw(_("Party Type is mandatory"))

			if not self.party:
				frappe.throw(_("Party is mandatory"))

			_party_name = "title" if self.party_type in ("Student", "Shareholder") else self.party_type.lower() + "_name"
			self.party_name = frappe.db.get_value(self.party_type, self.party, _party_name)

		if self.party:
			if not self.party_balance:
				self.party_balance = get_balance_on(party_type=self.party_type,
					party=self.party, date=self.posting_date, company=self.company)

			if not self.party_account:
				party_account = get_party_account(self.party_type, self.party, self.company)
				self.set(self.party_account_field, party_account)
				self.party_account = party_account

		if self.paid_from and not (self.paid_from_account_currency or self.paid_from_account_balance):
			acc = get_account_details(self.paid_from, self.posting_date, self.cost_center)
			self.paid_from_account_currency = acc.account_currency
			self.paid_from_account_balance = acc.account_balance

		if self.paid_to and not (self.paid_to_account_currency or self.paid_to_account_balance):
			acc = get_account_details(self.paid_to, self.posting_date, self.cost_center)
			self.paid_to_account_currency = acc.account_currency
			self.paid_to_account_balance = acc.account_balance

		self.party_account_currency = self.paid_from_account_currency \
			if self.payment_type=="Receive" else self.paid_to_account_currency

		self.set_missing_ref_details()

	def set_missing_ref_details(self, force=False):
		for d in self.get("references"):
			if d.allocated_amount:
				ref_details = get_reference_details(d.reference_doctype,
					d.reference_name, self.party_account_currency)

				for field, value in iteritems(ref_details):
					if field == 'exchange_rate' or not d.get(field) or force:
						d.set(field, value)

	def validate_payment_type(self):
		if self.payment_type not in ("Receive", "Pay", "Internal Transfer"):
			frappe.throw(_("Payment Type must be one of Receive, Pay and Internal Transfer"))

	def validate_party_details(self):
		if self.party:
			if not frappe.db.exists(self.party_type, self.party):
				frappe.throw(_("Invalid {0}: {1}").format(self.party_type, self.party))

			if self.party_account and self.party_type in ("Customer", "Supplier"):
				self.validate_account_type(self.party_account,
					[erpnext.get_party_account_type(self.party_type)])

	def validate_bank_accounts(self):
		if self.payment_type in ("Pay", "Internal Transfer"):
			self.validate_account_type(self.paid_from, ["Bank", "Cash"])

		if self.payment_type in ("Receive", "Internal Transfer"):
			self.validate_account_type(self.paid_to, ["Bank", "Cash"])

	def validate_account_type(self, account, account_types):
		account_type = frappe.db.get_value("Account", account, "account_type")
		# if account_type not in account_types:
		# 	frappe.throw(_("Account Type for {0} must be {1}").format(account, comma_or(account_types)))

	def set_exchange_rate(self, ref_doc=None):
		self.set_source_exchange_rate(ref_doc)
		self.set_target_exchange_rate(ref_doc)

	def set_source_exchange_rate(self, ref_doc=None):
		if self.paid_from and not self.source_exchange_rate:
			if self.paid_from_account_currency == self.company_currency:
				self.source_exchange_rate = 1
			else:
				if ref_doc:
					if self.paid_from_account_currency == ref_doc.currency:
						self.source_exchange_rate = ref_doc.get("exchange_rate")

			if not self.source_exchange_rate:
					self.source_exchange_rate = get_exchange_rate(self.paid_from_account_currency,
						self.company_currency, self.posting_date)

	def set_target_exchange_rate(self, ref_doc=None):
		if self.paid_to and not self.target_exchange_rate:
			if ref_doc:
				if self.paid_to_account_currency == ref_doc.currency:
					self.target_exchange_rate = ref_doc.get("exchange_rate")

			if not self.target_exchange_rate:
				self.target_exchange_rate = get_exchange_rate(self.paid_to_account_currency,
					self.company_currency, self.posting_date)

	def validate_mandatory(self):
		for field in ("paid_amount", "received_amount", "source_exchange_rate", "target_exchange_rate"):
			if not self.get(field):
				frappe.throw(_("{0} is mandatory").format(self.meta.get_label(field)))

	def validate_reference_documents(self):
		if self.party_type == "Student":
			valid_reference_doctypes = ("Fees")
		elif self.party_type == "Customer":
			valid_reference_doctypes = ("Sales Order", "Sales Invoice", "Journal Entry", "Dunning")
		elif self.party_type == "Supplier":
			valid_reference_doctypes = ("Purchase Order", "Purchase Invoice", "Journal Entry")
		elif self.party_type == "Employee":
			valid_reference_doctypes = ("Expense Claim", "Journal Entry", "Employee Advance")
		elif self.party_type == "Shareholder":
			valid_reference_doctypes = ("Journal Entry")

		for d in self.get("references"):
			if not d.allocated_amount:
				continue
			if d.reference_doctype not in valid_reference_doctypes:
				frappe.throw(_("Reference Doctype must be one of {0}")
					.format(comma_or(valid_reference_doctypes)))

			elif d.reference_name:
				if not frappe.db.exists(d.reference_doctype, d.reference_name):
					frappe.throw(_("{0} {1} does not exist").format(d.reference_doctype, d.reference_name))
				else:
					ref_doc = frappe.get_doc(d.reference_doctype, d.reference_name)

					if d.reference_doctype != "Journal Entry":
						if self.party != ref_doc.get(scrub(self.party_type)):
							frappe.throw(_("{0} {1} is not associated with {2} {3}")
								.format(d.reference_doctype, d.reference_name, self.party_type, self.party))
					else:
						self.validate_journal_entry()

					if d.reference_doctype in ("Sales Invoice", "Purchase Invoice", "Expense Claim", "Fees"):
						if self.party_type == "Customer":
							ref_party_account = get_party_account_based_on_invoice_discounting(d.reference_name) or ref_doc.debit_to
						elif self.party_type == "Student":
							ref_party_account = ref_doc.receivable_account
						elif self.party_type=="Supplier":
							ref_party_account = ref_doc.credit_to
						elif self.party_type=="Employee":
							ref_party_account = ref_doc.payable_account

						if ref_party_account != self.party_account:
								frappe.throw(_("{0} {1} is associated with {2}, but Party Account is {3}")
									.format(d.reference_doctype, d.reference_name, ref_party_account, self.party_account))

					if ref_doc.docstatus != 1:
						frappe.throw(_("{0} {1} must be submitted")
							.format(d.reference_doctype, d.reference_name))

	def validate_paid_invoices(self):
		no_oustanding_refs = {}

		for d in self.get("references"):
			if not d.allocated_amount:
				continue

			if d.reference_doctype in ("Sales Invoice", "Purchase Invoice", "Fees"):
				outstanding_amount, is_return = frappe.get_cached_value(d.reference_doctype, d.reference_name, ["outstanding_amount", "is_return"])
				if outstanding_amount <= 0 and not is_return:
					no_oustanding_refs.setdefault(d.reference_doctype, []).append(d)

		for k, v in no_oustanding_refs.items():
			frappe.msgprint(
				_("{} - {} now have {} as they had no outstanding amount left before submitting the Payment Entry.")
					.format(k, frappe.bold(", ".join([d.reference_name for d in v])), frappe.bold("negative outstanding amount"))
				+ "<br><br>" + _("If this is undesirable please cancel the corresponding Payment Entry."),
				title=_("Warning"), indicator="orange")


	def validate_journal_entry(self):
		for d in self.get("references"):
			if d.allocated_amount and d.reference_doctype == "Journal Entry":
				je_accounts = frappe.db.sql("""select debit, credit from `tabJournal Entry Account`
					where account = %s and party=%s and docstatus = 1 and parent = %s
					and (reference_type is null or reference_type in ("", "Sales Order", "Purchase Order"))
					""", (self.party_account, self.party, d.reference_name), as_dict=True)

				if not je_accounts:
					frappe.throw(_("Row #{0}: Journal Entry {1} does not have account {2} or already matched against another voucher")
						.format(d.idx, d.reference_name, self.party_account))
				else:
					dr_or_cr = "debit" if self.payment_type == "Receive" else "credit"
					valid = False
					for jvd in je_accounts:
						if flt(jvd[dr_or_cr]) > 0:
							valid = True
					if not valid:
						frappe.throw(_("Against Journal Entry {0} does not have any unmatched {1} entry")
							.format(d.reference_name, dr_or_cr))

	def update_payment_schedule(self, cancel=0):
		invoice_payment_amount_map = {}
		invoice_paid_amount_map = {}

		for reference in self.get('references'):
			if reference.payment_term and reference.reference_name:
				key = (reference.payment_term, reference.reference_name)
				invoice_payment_amount_map.setdefault(key, 0.0)
				invoice_payment_amount_map[key] += reference.allocated_amount

				if not invoice_paid_amount_map.get(key):
					payment_schedule = frappe.get_all('Payment Schedule', filters={'parent': reference.reference_name},
						fields=['paid_amount', 'payment_amount', 'payment_term'])
					for term in payment_schedule:
						invoice_key = (term.payment_term, reference.reference_name)
						invoice_paid_amount_map.setdefault(invoice_key, {})
						invoice_paid_amount_map[invoice_key]['outstanding'] = term.payment_amount - term.paid_amount

		for key, amount in iteritems(invoice_payment_amount_map):
			if cancel:
				frappe.db.sql(""" UPDATE `tabPayment Schedule` SET paid_amount = `paid_amount` - %s
					WHERE parent = %s and payment_term = %s""", (amount, key[1], key[0]))
			else:
				outstanding = flt(invoice_paid_amount_map.get(key, {}).get('outstanding'))

				if amount > outstanding:
					frappe.throw(_('Cannot allocate more than {0} against payment term {1}').format(outstanding, key[0]))

				if amount and outstanding:
					frappe.db.sql(""" UPDATE `tabPayment Schedule` SET paid_amount = `paid_amount` + %s
							WHERE parent = %s and payment_term = %s""", (amount, key[1], key[0]))

	def set_status(self):
		if self.docstatus == 2:
			self.status = 'Cancelled'
		elif self.docstatus == 1:
			self.status = 'Submitted'
		else:
			self.status = 'Draft'

	def set_amounts(self):
		self.set_amounts_in_company_currency()
		self.set_total_allocated_amount()
		self.set_unallocated_amount()
		self.set_difference_amount()

	def set_amounts_in_company_currency(self):
		self.base_paid_amount, self.base_received_amount, self.difference_amount = 0, 0, 0
		if self.paid_amount:
			self.base_paid_amount = flt(flt(self.paid_amount) * flt(self.source_exchange_rate),
				self.precision("base_paid_amount"))

		if self.received_amount:
			self.base_received_amount = flt(flt(self.received_amount) * flt(self.target_exchange_rate),
				self.precision("base_received_amount"))

	def set_total_allocated_amount(self):
		if self.payment_type == "Internal Transfer":
			return

		total_allocated_amount, base_total_allocated_amount = 0, 0
		for d in self.get("references"):
			if d.allocated_amount:
				total_allocated_amount += flt(d.allocated_amount)
				base_total_allocated_amount += flt(flt(d.allocated_amount) * flt(d.exchange_rate),
					self.precision("base_paid_amount"))

		self.total_allocated_amount = abs(total_allocated_amount)
		self.base_total_allocated_amount = abs(base_total_allocated_amount)

	def set_unallocated_amount(self):
		self.unallocated_amount = 0
		if self.party:
			total_deductions = sum([flt(d.amount) for d in self.get("deductions")])
			if self.payment_type == "Receive" \
				and self.base_total_allocated_amount < self.base_received_amount + total_deductions \
				and self.total_allocated_amount < self.paid_amount + (total_deductions / self.source_exchange_rate):
					self.unallocated_amount = (self.base_received_amount + total_deductions -
						self.base_total_allocated_amount) / self.source_exchange_rate
			elif self.payment_type == "Pay" \
				and self.base_total_allocated_amount < (self.base_paid_amount - total_deductions) \
				and self.total_allocated_amount < self.received_amount + (total_deductions / self.target_exchange_rate):
					self.unallocated_amount = (self.base_paid_amount - (total_deductions +
						self.base_total_allocated_amount)) / self.target_exchange_rate

	def set_difference_amount(self):
		base_unallocated_amount = flt(self.unallocated_amount) * (flt(self.source_exchange_rate)
			if self.payment_type == "Receive" else flt(self.target_exchange_rate))

		base_party_amount = flt(self.base_total_allocated_amount) + flt(base_unallocated_amount)

		if self.payment_type == "Receive":
			self.difference_amount = base_party_amount - self.base_received_amount
		elif self.payment_type == "Pay":
			self.difference_amount = self.base_paid_amount - base_party_amount
		else:
			self.difference_amount = self.base_paid_amount - flt(self.base_received_amount)

		total_deductions = sum([flt(d.amount) for d in self.get("deductions")])

		self.difference_amount = flt(self.difference_amount - total_deductions,
			self.precision("difference_amount"))

	# Paid amount is auto allocated in the reference document by default.
	# Clear the reference document which doesn't have allocated amount on validate so that form can be loaded fast
	def clear_unallocated_reference_document_rows(self):
		self.set("references", self.get("references", {"allocated_amount": ["not in", [0, None, ""]]}))
		frappe.db.sql("""delete from `tabPayment Entry Reference`
			where parent = %s and allocated_amount = 0""", self.name)

	def validate_payment_against_negative_invoice(self):
		if ((self.payment_type=="Pay" and self.party_type=="Customer")
				or (self.payment_type=="Receive" and self.party_type=="Supplier")):

			total_negative_outstanding = sum([abs(flt(d.outstanding_amount))
				for d in self.get("references") if flt(d.outstanding_amount) < 0])

			paid_amount = self.paid_amount if self.payment_type=="Receive" else self.received_amount
			additional_charges = sum([flt(d.amount) for d in self.deductions])

			if not total_negative_outstanding:
				frappe.throw(_("Cannot {0} {1} {2} without any negative outstanding invoice")
					.format(self.payment_type, ("to" if self.party_type=="Customer" else "from"),
						self.party_type), InvalidPaymentEntry)

			elif paid_amount - additional_charges > total_negative_outstanding:
				frappe.throw(_("Paid Amount cannot be greater than total negative outstanding amount {0}")
					.format(total_negative_outstanding), InvalidPaymentEntry)

	def set_title(self):
		if self.payment_type in ("Receive", "Pay"):
			self.title = self.party
		else:
			self.title = self.paid_from + " - " + self.paid_to

	def validate_transaction_reference(self):
		bank_account = self.paid_to if self.payment_type == "Receive" else self.paid_from
		bank_account_type = frappe.db.get_value("Account", bank_account, "account_type")

		if bank_account_type == "Bank":
			if not self.reference_no or not self.reference_date:
				frappe.throw(_("Reference No and Reference Date is mandatory for Bank transaction"))

	def set_remarks(self):
		if self.custom_remarks: return

		if self.payment_type=="Internal Transfer":
			remarks = [_("Amount {0} {1} transferred from {2} to {3}")
				.format(self.paid_from_account_currency, self.paid_amount, self.paid_from, self.paid_to)]
		else:

			remarks = [_("Amount {0} {1} {2} {3}").format(
				self.party_account_currency,
				self.paid_amount if self.payment_type=="Receive" else self.received_amount,
				_("received from") if self.payment_type=="Receive" else _("to"), self.party
			)]

		if self.reference_no:
			remarks.append(_("Transaction reference no {0} dated {1}")
				.format(self.reference_no, self.reference_date))

		if self.payment_type in ["Receive", "Pay"]:
			for d in self.get("references"):
				if d.allocated_amount:
					remarks.append(_("Amount {0} {1} against {2} {3}").format(self.party_account_currency,
						d.allocated_amount, d.reference_doctype, d.reference_name))

		for d in self.get("deductions"):
			if d.amount:
				remarks.append(_("Amount {0} {1} deducted against {2}")
					.format(self.company_currency, d.amount, d.account))

		self.set("remarks", "\n".join(remarks))

	def make_gl_entries(self, cancel=0, adv_adj=0):
		if self.payment_type in ("Receive", "Pay") and not self.get("party_account_field"):
			self.setup_party_account_field()

		gl_entries = []
		self.add_party_gl_entries(gl_entries)
		self.add_bank_gl_entries(gl_entries)
		self.add_deductions_gl_entries(gl_entries)

		make_gl_entries(gl_entries, cancel=cancel, adv_adj=adv_adj)

	def add_party_gl_entries(self, gl_entries):
		if self.party_account:
			if self.payment_type=="Receive":
				against_account = self.paid_to
			else:
				against_account = self.paid_from

			party_gl_dict = self.get_gl_dict({
				"account": self.party_account,
				"party_type": self.party_type,
				"party": self.party,
				"against": against_account,
				"account_currency": self.party_account_currency,
				"cost_center": self.cost_center
			}, item=self)

			dr_or_cr = "credit" if erpnext.get_party_account_type(self.party_type) == 'Receivable' else "debit"

			for d in self.get("references"):
				gle = party_gl_dict.copy()
				gle.update({
					"against_voucher_type": d.reference_doctype,
					"against_voucher": d.reference_name
				})

				allocated_amount_in_company_currency = flt(flt(d.allocated_amount) * flt(d.exchange_rate),
					self.precision("paid_amount"))

				gle.update({
					dr_or_cr + "_in_account_currency": d.allocated_amount,
					dr_or_cr: allocated_amount_in_company_currency
				})

				gl_entries.append(gle)

			if self.unallocated_amount:
				base_unallocated_amount = base_unallocated_amount = self.unallocated_amount * \
					(self.source_exchange_rate if self.payment_type=="Receive" else self.target_exchange_rate)

				gle = party_gl_dict.copy()

				gle.update({
					dr_or_cr + "_in_account_currency": self.unallocated_amount,
					dr_or_cr: base_unallocated_amount
				})

				gl_entries.append(gle)

	def add_bank_gl_entries(self, gl_entries):
		if self.payment_type in ("Pay", "Internal Transfer"):
			gl_entries.append(
				self.get_gl_dict({
					"account": self.paid_from,
					"account_currency": self.paid_from_account_currency,
					"against": self.party if self.payment_type=="Pay" else self.paid_to,
					"credit_in_account_currency": self.paid_amount,
					"credit": self.base_paid_amount,
					"cost_center": self.cost_center
				}, item=self)
			)
		if self.payment_type in ("Receive", "Internal Transfer"):
			gl_entries.append(
				self.get_gl_dict({
					"account": self.paid_to,
					"account_currency": self.paid_to_account_currency,
					"against": self.party if self.payment_type=="Receive" else self.paid_from,
					"debit_in_account_currency": self.received_amount,
					"debit": self.base_received_amount,
					"cost_center": self.cost_center
				}, item=self)
			)

	def add_deductions_gl_entries(self, gl_entries):
		for d in self.get("deductions"):
			if d.amount:
				account_currency = get_account_currency(d.account)
				if account_currency != self.company_currency:
					frappe.throw(_("Currency for {0} must be {1}").format(d.account, self.company_currency))

				gl_entries.append(
					self.get_gl_dict({
						"account": d.account,
						"account_currency": account_currency,
						"against": self.party or self.paid_from,
						"debit_in_account_currency": d.amount,
						"debit": d.amount,
						"cost_center": d.cost_center
					}, item=d)
				)

	def update_advance_paid(self):
		if self.payment_type in ("Receive", "Pay") and self.party:
			for d in self.get("references"):
				if d.allocated_amount \
					and d.reference_doctype in ("Sales Order", "Purchase Order", "Employee Advance"):
						frappe.get_doc(d.reference_doctype, d.reference_name).set_total_advance_paid()

	def update_expense_claim(self):
		if self.payment_type in ("Pay") and self.party:
			for d in self.get("references"):
				if d.reference_doctype=="Expense Claim" and d.reference_name:
					doc = frappe.get_doc("Expense Claim", d.reference_name)
					update_reimbursed_amount(doc, self.name)

	def on_recurring(self, reference_doc, auto_repeat_doc):
		self.reference_no = reference_doc.name
		self.reference_date = nowdate()

	def calculate_deductions(self, tax_details):
		return {
			"account": tax_details['tax']['account_head'],
			"cost_center": frappe.get_cached_value('Company',  self.company,  "cost_center"),
			"amount": self.total_allocated_amount * (tax_details['tax']['rate'] / 100)
		}

	def set_gain_or_loss(self, account_details=None):
		if not self.difference_amount:
			self.set_difference_amount()

		row = {
			'amount': self.difference_amount
		}

		if account_details:
			row.update(account_details)

		self.append('deductions', row)
		self.set_unallocated_amount()

@frappe.whitelist()
def get_outstanding_reference_documents(args):

	if isinstance(args, string_types):
		args = json.loads(args)

	if args.get('party_type') == 'Member':
		return

	# confirm that Supplier is not blocked
	if args.get('party_type') == 'Supplier':
		supplier_status = get_supplier_block_status(args['party'])
		if supplier_status['on_hold']:
			if supplier_status['hold_type'] == 'All':
				return []
			elif supplier_status['hold_type'] == 'Payments':
				if not supplier_status['release_date'] or getdate(nowdate()) <= supplier_status['release_date']:
					return []

	party_account_currency = get_account_currency(args.get("party_account"))
	company_currency = frappe.get_cached_value('Company',  args.get("company"),  "default_currency")

	# Get negative outstanding sales /purchase invoices
	negative_outstanding_invoices = []
	if args.get("party_type") not in ["Student", "Employee"] and not args.get("voucher_no"):
		negative_outstanding_invoices = get_negative_outstanding_invoices(args.get("party_type"), args.get("party"),
			args.get("party_account"), args.get("company"), party_account_currency, company_currency)

	# Get positive outstanding sales /purchase invoices/ Fees
	condition = ""
	if args.get("voucher_type") and args.get("voucher_no"):
		condition = " and voucher_type={0} and voucher_no={1}"\
			.format(frappe.db.escape(args["voucher_type"]), frappe.db.escape(args["voucher_no"]))

	# Add cost center condition
	if args.get("cost_center"):
		condition += " and cost_center='%s'" % args.get("cost_center")

	date_fields_dict = {
		'posting_date': ['from_posting_date', 'to_posting_date'],
		'due_date': ['from_due_date', 'to_due_date']
	}

	for fieldname, date_fields in date_fields_dict.items():
		if args.get(date_fields[0]) and args.get(date_fields[1]):
			condition += " and {0} between '{1}' and '{2}'".format(fieldname,
				args.get(date_fields[0]), args.get(date_fields[1]))

	if args.get("company"):
		condition += " and company = {0}".format(frappe.db.escape(args.get("company")))

	outstanding_invoices = get_outstanding_invoices(args.get("party_type"), args.get("party"),
		args.get("party_account"), filters=args, condition=condition)

	for d in outstanding_invoices:
		d["exchange_rate"] = 1
		if party_account_currency != company_currency:
			if d.voucher_type in ("Sales Invoice", "Purchase Invoice", "Expense Claim"):
				d["exchange_rate"] = frappe.db.get_value(d.voucher_type, d.voucher_no, "conversion_rate")
			elif d.voucher_type == "Journal Entry":
				d["exchange_rate"] = get_exchange_rate(
					party_account_currency,	company_currency, d.posting_date
				)
		if d.voucher_type in ("Purchase Invoice"):
			d["bill_no"] = frappe.db.get_value(d.voucher_type, d.voucher_no, "bill_no")

	# Get all SO / PO which are not fully billed or aginst which full advance not paid
	orders_to_be_billed = []
	if (args.get("party_type") != "Student"):
		orders_to_be_billed =  get_orders_to_be_billed(args.get("posting_date"),args.get("party_type"),
			args.get("party"), args.get("company"), party_account_currency, company_currency, filters=args)

	data = negative_outstanding_invoices + outstanding_invoices + orders_to_be_billed

	if not data:
		frappe.msgprint(_("No outstanding invoices found for the {0} {1} which qualify the filters you have specified.")
			.format(args.get("party_type").lower(), frappe.bold(args.get("party"))))

	return data


def get_orders_to_be_billed(posting_date, party_type, party,
	company, party_account_currency, company_currency, cost_center=None, filters=None):
	if party_type == "Customer":
		voucher_type = 'Sales Order'
	elif party_type == "Supplier":
		voucher_type = 'Purchase Order'
	elif party_type == "Employee":
		voucher_type = None

	# Add cost center condition
	if voucher_type:
		doc = frappe.get_doc({"doctype": voucher_type})
		condition = ""
		if doc and hasattr(doc, 'cost_center'):
			condition = " and cost_center='%s'" % cost_center

	orders = []
	if voucher_type:
		if party_account_currency == company_currency:
			grand_total_field = "base_grand_total"
			rounded_total_field = "base_rounded_total"
		else:
			grand_total_field = "grand_total"
			rounded_total_field = "rounded_total"

		orders = frappe.db.sql("""
			select
				name as voucher_no,
				if({rounded_total_field}, {rounded_total_field}, {grand_total_field}) as invoice_amount,
				(if({rounded_total_field}, {rounded_total_field}, {grand_total_field}) - advance_paid) as outstanding_amount,
				transaction_date as posting_date
			from
				`tab{voucher_type}`
			where
				{party_type} = %s
				and docstatus = 1
				and company = %s
				and ifnull(status, "") != "Closed"
				and if({rounded_total_field}, {rounded_total_field}, {grand_total_field}) > advance_paid
				and abs(100 - per_billed) > 0.01
				{condition}
			order by
				transaction_date, name
		""".format(**{
			"rounded_total_field": rounded_total_field,
			"grand_total_field": grand_total_field,
			"voucher_type": voucher_type,
			"party_type": scrub(party_type),
			"condition": condition
		}), (party, company), as_dict=True)

	order_list = []
	for d in orders:
		if not (flt(d.outstanding_amount) >= flt(filters.get("outstanding_amt_greater_than"))
			and flt(d.outstanding_amount) <= flt(filters.get("outstanding_amt_less_than"))):
			continue

		d["voucher_type"] = voucher_type
		# This assumes that the exchange rate required is the one in the SO
		d["exchange_rate"] = get_exchange_rate(party_account_currency, company_currency, posting_date)
		order_list.append(d)

	return order_list

def get_negative_outstanding_invoices(party_type, party, party_account,
	company, party_account_currency, company_currency, cost_center=None):
	voucher_type = "Sales Invoice" if party_type == "Customer" else "Purchase Invoice"
	supplier_condition = ""
	if voucher_type == "Purchase Invoice":
		supplier_condition = "and (release_date is null or release_date <= CURDATE())"
	if party_account_currency == company_currency:
		grand_total_field = "base_grand_total"
		rounded_total_field = "base_rounded_total"
	else:
		grand_total_field = "grand_total"
		rounded_total_field = "rounded_total"

	return frappe.db.sql("""
		select
			"{voucher_type}" as voucher_type, name as voucher_no,
			if({rounded_total_field}, {rounded_total_field}, {grand_total_field}) as invoice_amount,
			outstanding_amount, posting_date,
			due_date, conversion_rate as exchange_rate
		from
			`tab{voucher_type}`
		where
			{party_type} = %s and {party_account} = %s and docstatus = 1 and
			company = %s and outstanding_amount < 0
			{supplier_condition}
		order by
			posting_date, name
		""".format(**{
			"supplier_condition": supplier_condition,
			"rounded_total_field": rounded_total_field,
			"grand_total_field": grand_total_field,
			"voucher_type": voucher_type,
			"party_type": scrub(party_type),
			"party_account": "debit_to" if party_type == "Customer" else "credit_to",
			"cost_center": cost_center
		}), (party, party_account, company), as_dict=True)


@frappe.whitelist()
def get_party_details(company, party_type, party, date, cost_center=None):
	bank_account = ''
	if not frappe.db.exists(party_type, party):
		frappe.throw(_("Invalid {0}: {1}").format(party_type, party))

	party_account = get_party_account(party_type, party, company)

	account_currency = get_account_currency(party_account)
	account_balance = get_balance_on(party_account, date, cost_center=cost_center)
	_party_name = "title" if party_type in ("Student", "Shareholder") else party_type.lower() + "_name"
	party_name = frappe.db.get_value(party_type, party, _party_name)
	party_balance = get_balance_on(party_type=party_type, party=party, cost_center=cost_center)
	if party_type in ["Customer", "Supplier"]:
		bank_account = get_party_bank_account(party_type, party)

	return {
		"party_account": party_account,
		"party_name": party_name,
		"party_account_currency": account_currency,
		"party_balance": party_balance,
		"account_balance": account_balance,
		"bank_account": bank_account
	}


@frappe.whitelist()
def get_account_details(account, date, cost_center=None):
	frappe.has_permission('Payment Entry', throw=True)

	# to check if the passed account is accessible under reference doctype Payment Entry
	account_list = frappe.get_list('Account', {
		'name': account
	}, reference_doctype='Payment Entry', limit=1)

	# There might be some user permissions which will allow account under certain doctypes
	# except for Payment Entry, only in such case we should throw permission error
	if not account_list:
		frappe.throw(_('Account: {0} is not permitted under Payment Entry').format(account))

	account_balance = get_balance_on(account, date, cost_center=cost_center,
		ignore_account_permission=True)

	return frappe._dict({
		"account_currency": get_account_currency(account),
		"account_balance": account_balance,
		"account_type": frappe.db.get_value("Account", account, "account_type")
	})


@frappe.whitelist()
def get_company_defaults(company):
	fields = ["write_off_account", "exchange_gain_loss_account", "cost_center"]
	ret = frappe.get_cached_value('Company',  company,  fields, as_dict=1)

	for fieldname in fields:
		if not ret[fieldname]:
			frappe.throw(_("Please set default {0} in Company {1}")
				.format(frappe.get_meta("Company").get_label(fieldname), company))

	return ret


def get_outstanding_on_journal_entry(name):
	res = frappe.db.sql(
			'SELECT '
			'CASE WHEN party_type IN ("Customer", "Student") '
			'THEN ifnull(sum(debit_in_account_currency - credit_in_account_currency), 0) '
			'ELSE ifnull(sum(credit_in_account_currency - debit_in_account_currency), 0) '
			'END as outstanding_amount '
			'FROM `tabGL Entry` WHERE (voucher_no=%s OR against_voucher=%s) '
			'AND party_type IS NOT NULL '
			'AND party_type != ""',
			(name, name), as_dict=1
		)

	outstanding_amount = res[0].get('outstanding_amount', 0) if res else 0

	return outstanding_amount


@frappe.whitelist()
def get_reference_details(reference_doctype, reference_name, party_account_currency):
	total_amount = outstanding_amount = exchange_rate = bill_no = None
	ref_doc = frappe.get_doc(reference_doctype, reference_name)
	company_currency = ref_doc.get("company_currency") or erpnext.get_company_currency(ref_doc.company)

	if reference_doctype == "Fees":
		total_amount = ref_doc.get("grand_total")
		exchange_rate = 1
		outstanding_amount = ref_doc.get("outstanding_amount")
	elif reference_doctype == "Dunning":
		total_amount = ref_doc.get("dunning_amount")
		exchange_rate = 1
		outstanding_amount = ref_doc.get("dunning_amount")
	elif reference_doctype == "Journal Entry" and ref_doc.docstatus == 1:
		total_amount = ref_doc.get("total_amount")
		if ref_doc.multi_currency:
			exchange_rate = get_exchange_rate(party_account_currency, company_currency, ref_doc.posting_date)
		else:
			exchange_rate = 1
			outstanding_amount = get_outstanding_on_journal_entry(reference_name)
	elif reference_doctype != "Journal Entry":
		if ref_doc.doctype == "Expense Claim":
				total_amount = flt(ref_doc.total_sanctioned_amount) + flt(ref_doc.total_taxes_and_charges)
		elif ref_doc.doctype == "Employee Advance":
			total_amount = ref_doc.advance_amount
			exchange_rate = ref_doc.get("exchange_rate")
			if party_account_currency != ref_doc.currency:
				total_amount = flt(total_amount) * flt(exchange_rate)
		if not total_amount:
			if party_account_currency == company_currency:
				total_amount = ref_doc.base_grand_total
				exchange_rate = 1
			else:
				total_amount = ref_doc.grand_total
		if not exchange_rate:
			# Get the exchange rate from the original ref doc
			# or get it based on the posting date of the ref doc.
			exchange_rate = ref_doc.get("conversion_rate") or \
				get_exchange_rate(party_account_currency, company_currency, ref_doc.posting_date)
		if reference_doctype in ("Sales Invoice", "Purchase Invoice"):
			outstanding_amount = ref_doc.get("outstanding_amount")
			bill_no = ref_doc.get("bill_no")
		elif reference_doctype == "Expense Claim":
			outstanding_amount = flt(ref_doc.get("total_sanctioned_amount")) + flt(ref_doc.get("total_taxes_and_charges"))\
				- flt(ref_doc.get("total_amount_reimbursed")) - flt(ref_doc.get("total_advance_amount"))
		elif reference_doctype == "Employee Advance":
			outstanding_amount = (flt(ref_doc.advance_amount) - flt(ref_doc.paid_amount))
			if party_account_currency != ref_doc.currency:
				outstanding_amount = flt(outstanding_amount) * flt(exchange_rate)
				if party_account_currency == company_currency:
					exchange_rate = 1
		else:
			outstanding_amount = flt(total_amount) - flt(ref_doc.advance_paid)
	else:
		# Get the exchange rate based on the posting date of the ref doc.
		exchange_rate = get_exchange_rate(party_account_currency,
			company_currency, ref_doc.posting_date)

	return frappe._dict({
		"due_date": ref_doc.get("due_date"),
		"total_amount": total_amount,
		"outstanding_amount": outstanding_amount,
		"exchange_rate": exchange_rate,
		"bill_no": bill_no
	})

def get_amounts_based_on_reference_doctype(reference_doctype, ref_doc, party_account_currency, company_currency, reference_name):
	total_amount, outstanding_amount, exchange_rate = None
	if reference_doctype == "Fees":
		total_amount = ref_doc.get("grand_total")
		exchange_rate = 1
		outstanding_amount = ref_doc.get("outstanding_amount")
	elif reference_doctype == "Dunning":
		total_amount = ref_doc.get("dunning_amount")
		exchange_rate = 1
		outstanding_amount = ref_doc.get("dunning_amount")
	elif reference_doctype == "Journal Entry" and ref_doc.docstatus == 1:
		total_amount = ref_doc.get("total_amount")
		if ref_doc.multi_currency:
			exchange_rate = get_exchange_rate(party_account_currency, company_currency, ref_doc.posting_date)
		else:
			exchange_rate = 1
			outstanding_amount = get_outstanding_on_journal_entry(reference_name)

	return total_amount, outstanding_amount, exchange_rate

def get_amounts_based_on_ref_doc(reference_doctype, ref_doc, party_account_currency, company_currency):
	total_amount, outstanding_amount, exchange_rate = None
	if ref_doc.doctype == "Expense Claim":
			total_amount = flt(ref_doc.total_sanctioned_amount) + flt(ref_doc.total_taxes_and_charges)
	elif ref_doc.doctype == "Employee Advance":
		total_amount, exchange_rate = get_total_amount_exchange_rate_for_employee_advance(party_account_currency, ref_doc)
		
	if not total_amount:
		total_amount, exchange_rate = get_total_amount_exchange_rate_base_on_currency(
			party_account_currency, company_currency, ref_doc)

	if not exchange_rate:
		# Get the exchange rate from the original ref doc
		# or get it based on the posting date of the ref doc
		exchange_rate = ref_doc.get("conversion_rate") or \
			get_exchange_rate(party_account_currency, company_currency, ref_doc.posting_date)

	outstanding_amount, exchange_rate, bill_no = get_bill_no_and_update_amounts(
		reference_doctype, ref_doc, total_amount, exchange_rate, party_account_currency, company_currency)

	return total_amount, outstanding_amount, exchange_rate, bill_no

def get_total_amount_exchange_rate_for_employee_advance(party_account_currency, ref_doc):
	total_amount = ref_doc.advance_amount
	exchange_rate = ref_doc.get("exchange_rate")
	if party_account_currency != ref_doc.currency:
		total_amount = flt(total_amount) * flt(exchange_rate)

	return total_amount, exchange_rate

def get_total_amount_exchange_rate_base_on_currency(party_account_currency, company_currency, ref_doc):
	exchange_rate = None
	if party_account_currency == company_currency:
		total_amount = ref_doc.base_grand_total
		exchange_rate = 1
	else:
		total_amount = ref_doc.grand_total

	return total_amount, exchange_rate

def get_bill_no_and_update_amounts(reference_doctype, ref_doc, total_amount, exchange_rate, party_account_currency, company_currency):
	outstanding_amount, bill_no = None
	if reference_doctype in ("Sales Invoice", "Purchase Invoice"):
		outstanding_amount = ref_doc.get("outstanding_amount")
		bill_no = ref_doc.get("bill_no")
	elif reference_doctype == "Expense Claim":
		outstanding_amount = flt(ref_doc.get("total_sanctioned_amount")) + flt(ref_doc.get("total_taxes_and_charges"))\
			- flt(ref_doc.get("total_amount_reimbursed")) - flt(ref_doc.get("total_advance_amount"))
	elif reference_doctype == "Employee Advance":
		outstanding_amount = (flt(ref_doc.advance_amount) - flt(ref_doc.paid_amount))
		if party_account_currency != ref_doc.currency:
			outstanding_amount = flt(outstanding_amount) * flt(exchange_rate)
			if party_account_currency == company_currency:
				exchange_rate = 1
	else:
		outstanding_amount = flt(total_amount) - flt(ref_doc.advance_paid)

	return outstanding_amount, exchange_rate, bill_no


@frappe.whitelist()
def get_payment_entry(dt, dn, party_amount=None, bank_account=None, bank_amount=None):
	reference_doc = None
	doc = frappe.get_doc(dt, dn)
	if dt in ("Sales Order", "Purchase Order") and flt(doc.per_billed, 2) > 0:
		frappe.throw(_("Can only make payment against unbilled {0}").format(dt))

	party_type = set_party_type(dt)
	party_account = set_party_account(dt, dn, doc, party_type)
	party_account_currency = set_party_account_currency(dt, party_account, doc)
	payment_type = set_payment_type(dt, doc)
	grand_total, outstanding_amount = set_grand_total_and_outstanding_amount(party_amount, dt, party_account_currency, doc)

	# bank or cash
	bank = get_bank_cash_account(doc, bank_account)

	paid_amount, received_amount = set_paid_amount_and_received_amount(
		dt, party_account_currency, bank, outstanding_amount, payment_type, bank_amount, doc)

	pe = frappe.new_doc("Payment Entry")
	pe.payment_type = payment_type
	pe.company = doc.company
	pe.cost_center = doc.get("cost_center")
	pe.posting_date = nowdate()
	pe.mode_of_payment = doc.get("mode_of_payment")
	pe.party_type = party_type
	pe.party = doc.get(scrub(party_type))
	pe.contact_person = doc.get("contact_person")
	pe.contact_email = doc.get("contact_email")
	pe.ensure_supplier_is_not_blocked()

	pe.paid_from = party_account if payment_type=="Receive" else bank.account
	pe.paid_to = party_account if payment_type=="Pay" else bank.account
	pe.paid_from_account_currency = party_account_currency \
		if payment_type=="Receive" else bank.account_currency
	pe.paid_to_account_currency = party_account_currency if payment_type=="Pay" else bank.account_currency
	pe.paid_amount = paid_amount
	pe.received_amount = received_amount
	pe.letter_head = doc.get("letter_head")

	if pe.party_type in ["Customer", "Supplier"]:
		bank_account = get_party_bank_account(pe.party_type, pe.party)
		pe.set("bank_account", bank_account)
		pe.set_bank_account_data()

	# only Purchase Invoice can be blocked individually
	if doc.doctype == "Purchase Invoice" and doc.invoice_is_blocked():
		frappe.msgprint(_('{0} is on hold till {1}').format(doc.name, doc.release_date))
	else:
		if (doc.doctype in ('Sales Invoice', 'Purchase Invoice')
			and frappe.get_value('Payment Terms Template',
			{'name': doc.payment_terms_template}, 'allocate_payment_based_on_payment_terms')):

			for reference in get_reference_as_per_payment_terms(doc.payment_schedule, dt, dn, doc, grand_total, outstanding_amount):
				pe.append('references', reference)
		else:
			if dt == "Dunning":
				pe.append("references", {
					'reference_doctype': 'Sales Invoice',
					'reference_name': doc.get('sales_invoice'),
					"bill_no": doc.get("bill_no"),
					"due_date": doc.get("due_date"),
					'total_amount': doc.get('outstanding_amount'),
					'outstanding_amount': doc.get('outstanding_amount'),
					'allocated_amount': doc.get('outstanding_amount')
				})
				pe.append("references", {
					'reference_doctype': dt,
					'reference_name': dn,
					"bill_no": doc.get("bill_no"),
					"due_date": doc.get("due_date"),
					'total_amount': doc.get('dunning_amount'),
					'outstanding_amount': doc.get('dunning_amount'),
					'allocated_amount': doc.get('dunning_amount')
				})
			else:
				pe.append("references", {
					'reference_doctype': dt,
					'reference_name': dn,
					"bill_no": doc.get("bill_no"),
					"due_date": doc.get("due_date"),
					'total_amount': grand_total,
					'outstanding_amount': outstanding_amount,
					'allocated_amount': outstanding_amount
				})

	pe.setup_party_account_field()
	pe.set_missing_values()
	if party_account and bank:
		if dt == "Employee Advance":
			reference_doc = doc
		pe.set_exchange_rate(ref_doc=reference_doc)
		pe.set_amounts()
	return pe

def get_bank_cash_account(doc, bank_account):
	bank = get_default_bank_cash_account(doc.company, "Bank", mode_of_payment=doc.get("mode_of_payment"),
		account=bank_account)

	if not bank:
		bank = get_default_bank_cash_account(doc.company, "Cash", mode_of_payment=doc.get("mode_of_payment"),
			account=bank_account)

	return bank

def set_party_type(dt):
	if dt in ("Sales Invoice", "Sales Order", "Dunning"):
		party_type = "Customer"
	elif dt in ("Purchase Invoice", "Purchase Order"):
		party_type = "Supplier"
	elif dt in ("Expense Claim", "Employee Advance"):
		party_type = "Employee"
	elif dt in ("Fees"):
		party_type = "Student"
	return party_type

def set_party_account(dt, dn, doc, party_type):
	if dt == "Sales Invoice":
		party_account = get_party_account_based_on_invoice_discounting(dn) or doc.debit_to
	elif dt == "Purchase Invoice":
		party_account = doc.credit_to
	elif dt == "Fees":
		party_account = doc.receivable_account
	elif dt == "Employee Advance":
		party_account = doc.advance_account
	elif dt == "Expense Claim":
		party_account = doc.payable_account
	else:
		party_account = get_party_account(party_type, doc.get(party_type.lower()), doc.company)
	return party_account

def set_party_account_currency(dt, party_account, doc):
	if dt not in ("Sales Invoice", "Purchase Invoice"):
		party_account_currency = get_account_currency(party_account)
	else:
		party_account_currency = doc.get("party_account_currency") or get_account_currency(party_account)
	return party_account_currency

def set_payment_type(dt, doc):
	if (dt == "Sales Order" or (dt in ("Sales Invoice", "Fees", "Dunning") and doc.outstanding_amount > 0)) \
		or (dt=="Purchase Invoice" and doc.outstanding_amount < 0):
			payment_type = "Receive"
	else:
		payment_type = "Pay"
	return payment_type

def set_grand_total_and_outstanding_amount(party_amount, dt, party_account_currency, doc):
	grand_total = outstanding_amount = 0
	if party_amount:
		grand_total = outstanding_amount = party_amount
	elif dt in ("Sales Invoice", "Purchase Invoice"):
		if party_account_currency == doc.company_currency:
			grand_total = doc.base_rounded_total or doc.base_grand_total
		else:
			grand_total = doc.rounded_total or doc.grand_total
		outstanding_amount = doc.outstanding_amount
	elif dt in ("Expense Claim"):
		grand_total = doc.total_sanctioned_amount + doc.total_taxes_and_charges
		outstanding_amount = doc.grand_total \
			- doc.total_amount_reimbursed
	elif dt == "Employee Advance":
		grand_total = flt(doc.advance_amount)
		outstanding_amount = flt(doc.advance_amount) - flt(doc.paid_amount)
		if party_account_currency != doc.currency:
			grand_total = flt(doc.advance_amount) * flt(doc.exchange_rate)
			outstanding_amount = (flt(doc.advance_amount) - flt(doc.paid_amount)) * flt(doc.exchange_rate)
	elif dt == "Fees":
		grand_total = doc.grand_total
		outstanding_amount = doc.outstanding_amount
	elif dt == "Dunning":
		grand_total = doc.grand_total
		outstanding_amount = doc.grand_total
	else:
		if party_account_currency == doc.company_currency:
			grand_total = flt(doc.get("base_rounded_total") or doc.base_grand_total)
		else:
			grand_total = flt(doc.get("rounded_total") or doc.grand_total)
		outstanding_amount = grand_total - flt(doc.advance_paid)
	return grand_total, outstanding_amount

def set_paid_amount_and_received_amount(dt, party_account_currency, bank, outstanding_amount, payment_type, bank_amount, doc):
	paid_amount = received_amount = 0
	if party_account_currency == bank.account_currency:
		paid_amount = received_amount = abs(outstanding_amount)
	elif payment_type == "Receive":
		paid_amount = abs(outstanding_amount)
		if bank_amount:
			received_amount = bank_amount
		else:
			received_amount = paid_amount * doc.get('conversion_rate', 1)
			if dt == "Employee Advance":
				received_amount = paid_amount * doc.get('exchange_rate', 1)
	else:
		received_amount = abs(outstanding_amount)
		if bank_amount:
			paid_amount = bank_amount
		else:
			# if party account currency and bank currency is different then populate paid amount as well
			paid_amount = received_amount * doc.get('conversion_rate', 1)
			if dt == "Employee Advance":
				paid_amount = received_amount * doc.get('exchange_rate', 1)
	return paid_amount, received_amount

def get_reference_as_per_payment_terms(payment_schedule, dt, dn, doc, grand_total, outstanding_amount):
	references = []
	for payment_term in payment_schedule:
		payment_term_outstanding = flt(payment_term.payment_amount - payment_term.paid_amount,
				payment_term.precision('payment_amount'))

		if payment_term_outstanding:
			references.append({
				'reference_doctype': dt,
				'reference_name': dn,
				'bill_no': doc.get('bill_no'),
				'due_date': doc.get('due_date'),
				'total_amount': grand_total,
				'outstanding_amount': outstanding_amount,
				'payment_term': payment_term.payment_term,
				'allocated_amount': payment_term_outstanding
			})

	return references

def get_paid_amount(dt, dn, party_type, party, account, due_date):
	if party_type=="Customer":
		dr_or_cr = "credit_in_account_currency - debit_in_account_currency"
	else:
		dr_or_cr = "debit_in_account_currency - credit_in_account_currency"

	paid_amount = frappe.db.sql("""
		select ifnull(sum({dr_or_cr}), 0) as paid_amount
		from `tabGL Entry`
		where against_voucher_type = %s
			and against_voucher = %s
			and party_type = %s
			and party = %s
			and account = %s
			and due_date = %s
			and {dr_or_cr} > 0
	""".format(dr_or_cr=dr_or_cr), (dt, dn, party_type, party, account, due_date))

	return paid_amount[0][0] if paid_amount else 0

@frappe.whitelist()
def get_party_and_account_balance(company, date, paid_from=None, paid_to=None, ptype=None, pty=None, cost_center=None):
	return frappe._dict({
		"party_balance": get_balance_on(party_type=ptype, party=pty, cost_center=cost_center),
		"paid_from_account_balance": get_balance_on(paid_from, date, cost_center=cost_center),
		"paid_to_account_balance": get_balance_on(paid_to, date=date, cost_center=cost_center)
	})

@frappe.whitelist()
def make_payment_order(source_name, target_doc=None):
	from frappe.model.mapper import get_mapped_doc
	def set_missing_values(source, target):
		target.payment_order_type = "Payment Entry"
		target.append('references', dict(
			reference_doctype="Payment Entry",
			reference_name=source.name,
			bank_account=source.party_bank_account,
			amount=source.paid_amount,
			account=source.paid_to,
			supplier=source.party,
			mode_of_payment=source.mode_of_payment,
		))

	doclist = get_mapped_doc("Payment Entry", source_name, {
		"Payment Entry": {
			"doctype": "Payment Order",
			"validation": {
				"docstatus": ["=", 1]
			},
		}

	}, target_doc, set_missing_values)

	return doclist