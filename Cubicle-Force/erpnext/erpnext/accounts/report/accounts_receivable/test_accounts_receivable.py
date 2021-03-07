from __future__ import unicode_literals
import frappe
import frappe.defaults
import unittest
from frappe.utils import today, getdate, add_days
from erpnext.accounts.report.accounts_receivable.accounts_receivable import execute
from erpnext.accounts.doctype.sales_invoice.test_sales_invoice import create_sales_invoice
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

class TestAccountsReceivable(unittest.TestCase):
	def test_accounts_receivable(self):
		frappe.db.sql("delete from `tabSales Invoice` where company='_Test Company 2'")
		frappe.db.sql("delete from `tabGL Entry` where company='_Test Company 2'")

		filters = {
			'company': '_Test Company 2',
			'based_on_payment_terms': 1,
			'report_date': today(),
			'range1': 30,
			'range2': 60,
			'range3': 90,
			'range4': 120
		}

		# check invoice grand total and invoiced column's value for 3 payment terms
		name = make_sales_invoice()
		report = execute(filters)

		expected_data = [[100, 30], [100, 50], [100, 20]]

		for i in range(3):
			row = report[1][i-1]
			self.assertEqual(expected_data[i-1], [row.invoice_grand_total, row.invoiced])

		# check invoice grand total, invoiced, paid and outstanding column's value after payment
		make_payment(name)
		report = execute(filters)

		expected_data_after_payment = [[100, 50, 10, 40], [100, 20, 0, 20]]

		for i in range(2):
			row = report[1][i-1]
			self.assertEqual(expected_data_after_payment[i-1],
				[row.invoice_grand_total, row.invoiced, row.paid, row.outstanding])

		# check invoice grand total, invoiced, paid and outstanding column's value after credit note
		make_credit_note(name)
		report = execute(filters)

		expected_data_after_credit_note = [100, 0, 0, 40, -40]

		row = report[1][0]
		self.assertEqual(expected_data_after_credit_note,
			[row.invoice_grand_total, row.invoiced, row.paid, row.credit_note, row.outstanding])

def make_sales_invoice():
	frappe.set_user("Administrator")

	si = create_sales_invoice(company="_Test Company 2",
			customer = '_Test Customer 2',
			currency = 'EUR',
			warehouse = 'Finished Goods - _TC2',
			debit_to = 'Debtors - _TC2',
			income_account = 'Sales - _TC2',
			expense_account = 'Cost of Goods Sold - _TC2',
			cost_center = 'Main - _TC2',
			do_not_save=1)

	si.append('payment_schedule', dict(due_date=getdate(add_days(today(), 30)), invoice_portion=30.00, payment_amount=30))
	si.append('payment_schedule', dict(due_date=getdate(add_days(today(), 60)), invoice_portion=50.00, payment_amount=50))
	si.append('payment_schedule', dict(due_date=getdate(add_days(today(), 90)), invoice_portion=20.00, payment_amount=20))

	si.submit()

	return si.name

def make_payment(docname):
	pe = get_payment_entry("Sales Invoice", docname, bank_account="Cash - _TC2", party_amount=40)
	pe.paid_from = "Debtors - _TC2"
	pe.insert()
	pe.submit()


def make_credit_note(docname):
	create_sales_invoice(company="_Test Company 2",
		customer = '_Test Customer 2',
		currency = 'EUR',
		qty = -1,
		warehouse = 'Finished Goods - _TC2',
		debit_to = 'Debtors - _TC2',
		income_account = 'Sales - _TC2',
		expense_account = 'Cost of Goods Sold - _TC2',
		cost_center = 'Main - _TC2',
		is_return = 1,
		return_against = docname)

