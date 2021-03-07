# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import erpnext
import unittest
from frappe.utils import (nowdate, add_days, getdate, now_datetime, add_to_date, get_datetime,
	add_months, get_first_day, get_last_day, flt, date_diff)
from erpnext.selling.doctype.customer.test_customer import get_customer_dict
from erpnext.payroll.doctype.salary_structure.test_salary_structure import make_employee
from erpnext.loan_management.doctype.process_loan_interest_accrual.process_loan_interest_accrual import (process_loan_interest_accrual_for_demand_loans,
	process_loan_interest_accrual_for_term_loans)
from erpnext.loan_management.doctype.loan_interest_accrual.loan_interest_accrual import days_in_year
from erpnext.loan_management.doctype.process_loan_security_shortfall.process_loan_security_shortfall import create_process_loan_security_shortfall
from erpnext.loan_management.doctype.loan.loan import unpledge_security, request_loan_closure, make_loan_write_off
from erpnext.loan_management.doctype.loan_security_unpledge.loan_security_unpledge import get_pledged_security_qty
from erpnext.loan_management.doctype.loan_application.loan_application import create_pledge
from erpnext.loan_management.doctype.loan_disbursement.loan_disbursement import get_disbursal_amount
from erpnext.loan_management.doctype.loan_repayment.loan_repayment import calculate_amounts
from erpnext.payroll.doctype.salary_structure.test_salary_structure import make_salary_structure

class TestLoan(unittest.TestCase):
	def setUp(self):
		create_loan_accounts()
		create_loan_type("Personal Loan", 500000, 8.4,
			is_term_loan=1,
			mode_of_payment='Cash',
			payment_account='Payment Account - _TC',
			loan_account='Loan Account - _TC',
			interest_income_account='Interest Income Account - _TC',
			penalty_income_account='Penalty Income Account - _TC')

		create_loan_type("Stock Loan", 2000000, 13.5, 25, 1, 5, 'Cash', 'Payment Account - _TC', 'Loan Account - _TC',
			'Interest Income Account - _TC', 'Penalty Income Account - _TC')

		create_loan_type("Demand Loan", 2000000, 13.5, 25, 0, 5, 'Cash', 'Payment Account - _TC', 'Loan Account - _TC',
			'Interest Income Account - _TC', 'Penalty Income Account - _TC')

		create_loan_security_type()
		create_loan_security()

		create_loan_security_price("Test Security 1", 500, "Nos", get_datetime() , get_datetime(add_to_date(nowdate(), hours=24)))
		create_loan_security_price("Test Security 2", 250, "Nos", get_datetime() , get_datetime(add_to_date(nowdate(), hours=24)))

		self.applicant1 = make_employee("robert_loan@loan.com")
		make_salary_structure("Test Salary Structure Loan", "Monthly", employee=self.applicant1, currency='INR', company="_Test Company")
		if not frappe.db.exists("Customer", "_Test Loan Customer"):
			frappe.get_doc(get_customer_dict('_Test Loan Customer')).insert(ignore_permissions=True)

		self.applicant2 = frappe.db.get_value("Customer", {'name': '_Test Loan Customer'}, 'name')

		create_loan(self.applicant1, "Personal Loan", 280000, "Repay Over Number of Periods", 20)

	def test_loan(self):
		loan = frappe.get_doc("Loan", {"applicant":self.applicant1})
		self.assertEquals(loan.monthly_repayment_amount, 15052)
		self.assertEquals(loan.total_interest_payable, 21034)
		self.assertEquals(loan.total_payment, 301034)

		schedule = loan.repayment_schedule

		self.assertEqual(len(schedule), 20)

		for idx, principal_amount, interest_amount, balance_loan_amount in [[3, 13369, 1683, 227079], [19, 14941, 105, 0], [17, 14740, 312, 29785]]:
			self.assertEqual(schedule[idx].principal_amount, principal_amount)
			self.assertEqual(schedule[idx].interest_amount, interest_amount)
			self.assertEqual(schedule[idx].balance_loan_amount, balance_loan_amount)

		loan.repayment_method = "Repay Fixed Amount per Period"
		loan.monthly_repayment_amount = 14000
		loan.save()

		self.assertEquals(len(loan.repayment_schedule), 22)
		self.assertEquals(loan.total_interest_payable, 22712)
		self.assertEquals(loan.total_payment, 302712)

	def test_loan_with_security(self):

		pledge = [{
			"loan_security": "Test Security 1",
			"qty": 4000.00,
		}]

		loan_application = create_loan_application('_Test Company', self.applicant2,
			'Stock Loan', pledge, "Repay Over Number of Periods", 12)
		create_pledge(loan_application)

		loan = create_loan_with_security(self.applicant2, "Stock Loan", "Repay Over Number of Periods",
			12, loan_application)
		self.assertEquals(loan.loan_amount, 1000000)

	def test_loan_disbursement(self):
		pledge = [{
			"loan_security": "Test Security 1",
			"qty": 4000.00
		}]

		loan_application = create_loan_application('_Test Company', self.applicant2, 'Stock Loan', pledge, "Repay Over Number of Periods", 12)

		create_pledge(loan_application)

		loan = create_loan_with_security(self.applicant2, "Stock Loan", "Repay Over Number of Periods", 12, loan_application)
		self.assertEquals(loan.loan_amount, 1000000)

		loan.submit()

		loan_disbursement_entry1 = make_loan_disbursement_entry(loan.name, 500000)
		loan_disbursement_entry2 = make_loan_disbursement_entry(loan.name, 500000)

		loan = frappe.get_doc("Loan", loan.name)
		gl_entries1 = frappe.db.get_all("GL Entry",
			fields=["name"],
			filters = {'voucher_type': 'Loan Disbursement', 'voucher_no': loan_disbursement_entry1.name}
		)

		gl_entries2 = frappe.db.get_all("GL Entry",
			fields=["name"],
			filters = {'voucher_type': 'Loan Disbursement', 'voucher_no': loan_disbursement_entry2.name}
		)

		self.assertEquals(loan.status, "Disbursed")
		self.assertEquals(loan.disbursed_amount, 1000000)
		self.assertTrue(gl_entries1)
		self.assertTrue(gl_entries2)

	def test_regular_loan_repayment(self):
		pledge = [{
			"loan_security": "Test Security 1",
			"qty": 4000.00
		}]

		loan_application = create_loan_application('_Test Company', self.applicant2, 'Demand Loan', pledge)
		create_pledge(loan_application)

		loan = create_demand_loan(self.applicant2, "Demand Loan", loan_application, posting_date='2019-10-01')
		loan.submit()

		self.assertEquals(loan.loan_amount, 1000000)

		first_date = '2019-10-01'
		last_date = '2019-10-30'

		no_of_days = date_diff(last_date, first_date) + 1

		accrued_interest_amount = flt((loan.loan_amount * loan.rate_of_interest * no_of_days)
			/ (days_in_year(get_datetime(first_date).year) * 100), 2)

		make_loan_disbursement_entry(loan.name, loan.loan_amount, disbursement_date=first_date)

		process_loan_interest_accrual_for_demand_loans(posting_date = last_date)

		repayment_entry = create_repayment_entry(loan.name, self.applicant2, add_days(last_date, 10), 111119)
		repayment_entry.save()
		repayment_entry.submit()

		penalty_amount = (accrued_interest_amount * 5 * 25) / 100
		self.assertEquals(flt(repayment_entry.penalty_amount,0), flt(penalty_amount, 0))

		amounts = frappe.db.get_all('Loan Interest Accrual', {'loan': loan.name}, ['paid_interest_amount'])

		loan.load_from_db()

		total_interest_paid = amounts[0]['paid_interest_amount'] + amounts[1]['paid_interest_amount']
		self.assertEquals(amounts[1]['paid_interest_amount'], repayment_entry.interest_payable)
		self.assertEquals(flt(loan.total_principal_paid, 0), flt(repayment_entry.amount_paid -
			 penalty_amount - total_interest_paid, 0))

	def test_loan_closure(self):
		pledge = [{
			"loan_security": "Test Security 1",
			"qty": 4000.00
		}]

		loan_application = create_loan_application('_Test Company', self.applicant2, 'Demand Loan', pledge)
		create_pledge(loan_application)

		loan = create_demand_loan(self.applicant2, "Demand Loan", loan_application, posting_date='2019-10-01')
		loan.submit()

		self.assertEquals(loan.loan_amount, 1000000)

		first_date = '2019-10-01'
		last_date = '2019-10-30'

		no_of_days = date_diff(last_date, first_date) + 1

		# Adding 5 since repayment is made 5 days late after due date
		# and since payment type is loan closure so interest should be considered for those
		# 5 days as well though in grace period
		no_of_days += 5

		accrued_interest_amount = (loan.loan_amount * loan.rate_of_interest * no_of_days) \
			/ (days_in_year(get_datetime(first_date).year) * 100)

		make_loan_disbursement_entry(loan.name, loan.loan_amount, disbursement_date=first_date)
		process_loan_interest_accrual_for_demand_loans(posting_date = last_date)

		repayment_entry = create_repayment_entry(loan.name, self.applicant2, add_days(last_date, 5),
			flt(loan.loan_amount + accrued_interest_amount))

		repayment_entry.submit()

		amount = frappe.db.get_value('Loan Interest Accrual', {'loan': loan.name}, ['sum(paid_interest_amount)'])

		self.assertEquals(flt(amount, 0),flt(accrued_interest_amount, 0))
		self.assertEquals(flt(repayment_entry.penalty_amount, 5), 0)

		request_loan_closure(loan.name)
		loan.load_from_db()
		self.assertEquals(loan.status, "Loan Closure Requested")

	def test_loan_repayment_for_term_loan(self):
		pledges = [{
			"loan_security": "Test Security 2",
			"qty": 4000.00
		},
		{
			"loan_security": "Test Security 1",
			"qty": 2000.00
		}]

		loan_application = create_loan_application('_Test Company', self.applicant2, 'Stock Loan', pledges,
			"Repay Over Number of Periods", 12)
		create_pledge(loan_application)

		loan = create_loan_with_security(self.applicant2, "Stock Loan", "Repay Over Number of Periods", 12, loan_application,
			posting_date=add_months(nowdate(), -1))

		loan.submit()

		make_loan_disbursement_entry(loan.name, loan.loan_amount, disbursement_date=add_months(nowdate(), -1))

		process_loan_interest_accrual_for_term_loans(posting_date=nowdate())

		repayment_entry = create_repayment_entry(loan.name, self.applicant2, add_days(nowdate(), 5), 89768.75)

		repayment_entry.submit()

		amounts = frappe.db.get_value('Loan Interest Accrual', {'loan': loan.name}, ['paid_interest_amount',
			'paid_principal_amount'])

		self.assertEquals(amounts[0], 11250.00)
		self.assertEquals(amounts[1], 78303.00)

	def test_security_shortfall(self):
		pledges = [{
			"loan_security": "Test Security 2",
			"qty": 8000.00,
			"haircut": 50,
		}]

		loan_application = create_loan_application('_Test Company', self.applicant2,
			'Stock Loan', pledges, "Repay Over Number of Periods", 12)

		create_pledge(loan_application)

		loan = create_loan_with_security(self.applicant2, "Stock Loan", "Repay Over Number of Periods", 12, loan_application)
		loan.submit()

		make_loan_disbursement_entry(loan.name, loan.loan_amount)

		frappe.db.sql("""UPDATE `tabLoan Security Price` SET loan_security_price = 100
			where loan_security='Test Security 2'""")

		create_process_loan_security_shortfall()
		loan_security_shortfall = frappe.get_doc("Loan Security Shortfall", {"loan": loan.name})
		self.assertTrue(loan_security_shortfall)

		self.assertEquals(loan_security_shortfall.loan_amount, 1000000.00)
		self.assertEquals(loan_security_shortfall.security_value, 800000.00)
		self.assertEquals(loan_security_shortfall.shortfall_amount, 600000.00)

		frappe.db.sql(""" UPDATE `tabLoan Security Price` SET loan_security_price = 250
			where loan_security='Test Security 2'""")

	def test_loan_security_unpledge(self):
		pledge = [{
			"loan_security": "Test Security 1",
			"qty": 4000.00
		}]

		loan_application = create_loan_application('_Test Company', self.applicant2, 'Demand Loan', pledge)
		create_pledge(loan_application)

		loan = create_demand_loan(self.applicant2, "Demand Loan", loan_application, posting_date='2019-10-01')
		loan.submit()

		self.assertEquals(loan.loan_amount, 1000000)

		first_date = '2019-10-01'
		last_date = '2019-10-30'

		no_of_days = date_diff(last_date, first_date) + 1

		no_of_days += 5

		accrued_interest_amount = (loan.loan_amount * loan.rate_of_interest * no_of_days) \
			/ (days_in_year(get_datetime(first_date).year) * 100)

		make_loan_disbursement_entry(loan.name, loan.loan_amount, disbursement_date=first_date)
		process_loan_interest_accrual_for_demand_loans(posting_date = last_date)

		repayment_entry = create_repayment_entry(loan.name, self.applicant2, add_days(last_date, 5), flt(loan.loan_amount + accrued_interest_amount))
		repayment_entry.submit()

		request_loan_closure(loan.name)
		loan.load_from_db()
		self.assertEquals(loan.status, "Loan Closure Requested")

		unpledge_request = unpledge_security(loan=loan.name, save=1)
		unpledge_request.submit()
		unpledge_request.status = 'Approved'
		unpledge_request.save()
		loan.load_from_db()

		pledged_qty = get_pledged_security_qty(loan.name)

		self.assertEqual(loan.status, 'Closed')
		self.assertEquals(sum(pledged_qty.values()), 0)

		amounts = amounts = calculate_amounts(loan.name, add_days(last_date, 5))
		self.assertEqual(amounts['pending_principal_amount'], 0)
		self.assertEquals(amounts['payable_principal_amount'], 0.0)
		self.assertEqual(amounts['interest_amount'], 0)

	def test_partial_loan_security_unpledge(self):
		pledge = [{
			"loan_security": "Test Security 1",
			"qty": 2000.00
		},
		{
			"loan_security": "Test Security 2",
			"qty": 4000.00
		}]

		loan_application = create_loan_application('_Test Company', self.applicant2, 'Demand Loan', pledge)
		create_pledge(loan_application)

		loan = create_demand_loan(self.applicant2, "Demand Loan", loan_application, posting_date='2019-10-01')
		loan.submit()

		self.assertEquals(loan.loan_amount, 1000000)

		first_date = '2019-10-01'
		last_date = '2019-10-30'

		make_loan_disbursement_entry(loan.name, loan.loan_amount, disbursement_date=first_date)
		process_loan_interest_accrual_for_demand_loans(posting_date = last_date)

		repayment_entry = create_repayment_entry(loan.name, self.applicant2, add_days(last_date, 5), 600000)
		repayment_entry.submit()

		unpledge_map = {'Test Security 2': 2000}

		unpledge_request = unpledge_security(loan=loan.name, security_map = unpledge_map, save=1)
		unpledge_request.submit()
		unpledge_request.status = 'Approved'
		unpledge_request.save()
		unpledge_request.submit()
		unpledge_request.load_from_db()
		self.assertEqual(unpledge_request.docstatus, 1)

	def test_santined_loan_security_unpledge(self):
		pledge = [{
			"loan_security": "Test Security 1",
			"qty": 4000.00
		}]

		loan_application = create_loan_application('_Test Company', self.applicant2, 'Demand Loan', pledge)
		create_pledge(loan_application)

		loan = create_demand_loan(self.applicant2, "Demand Loan", loan_application, posting_date='2019-10-01')
		loan.submit()

		self.assertEquals(loan.loan_amount, 1000000)

		unpledge_map = {'Test Security 1': 4000}
		unpledge_request = unpledge_security(loan=loan.name, security_map = unpledge_map, save=1)
		unpledge_request.submit()
		unpledge_request.status = 'Approved'
		unpledge_request.save()
		unpledge_request.submit()

	def test_disbursal_check_with_shortfall(self):
		pledges = [{
			"loan_security": "Test Security 2",
			"qty": 8000.00,
			"haircut": 50,
		}]

		loan_application = create_loan_application('_Test Company', self.applicant2,
			'Stock Loan', pledges, "Repay Over Number of Periods", 12)

		create_pledge(loan_application)

		loan = create_loan_with_security(self.applicant2, "Stock Loan", "Repay Over Number of Periods", 12, loan_application)
		loan.submit()

		#Disbursing 7,00,000 from the allowed 10,00,000 according to security pledge
		make_loan_disbursement_entry(loan.name, 700000)

		frappe.db.sql("""UPDATE `tabLoan Security Price` SET loan_security_price = 100
			where loan_security='Test Security 2'""")

		create_process_loan_security_shortfall()
		loan_security_shortfall = frappe.get_doc("Loan Security Shortfall", {"loan": loan.name})
		self.assertTrue(loan_security_shortfall)

		self.assertEqual(get_disbursal_amount(loan.name), 0)

		frappe.db.sql(""" UPDATE `tabLoan Security Price` SET loan_security_price = 250
			where loan_security='Test Security 2'""")

	def test_disbursal_check_without_shortfall(self):
		pledges = [{
			"loan_security": "Test Security 2",
			"qty": 8000.00,
			"haircut": 50,
		}]

		loan_application = create_loan_application('_Test Company', self.applicant2,
			'Stock Loan', pledges, "Repay Over Number of Periods", 12)

		create_pledge(loan_application)

		loan = create_loan_with_security(self.applicant2, "Stock Loan", "Repay Over Number of Periods", 12, loan_application)
		loan.submit()

		#Disbursing 7,00,000 from the allowed 10,00,000 according to security pledge
		make_loan_disbursement_entry(loan.name, 700000)

		self.assertEqual(get_disbursal_amount(loan.name), 300000)

	def test_pending_loan_amount_after_closure_request(self):
		pledge = [{
			"loan_security": "Test Security 1",
			"qty": 4000.00
		}]

		loan_application = create_loan_application('_Test Company', self.applicant2, 'Demand Loan', pledge)
		create_pledge(loan_application)

		loan = create_demand_loan(self.applicant2, "Demand Loan", loan_application, posting_date='2019-10-01')
		loan.submit()

		self.assertEquals(loan.loan_amount, 1000000)

		first_date = '2019-10-01'
		last_date = '2019-10-30'

		no_of_days = date_diff(last_date, first_date) + 1

		no_of_days += 5

		accrued_interest_amount = (loan.loan_amount * loan.rate_of_interest * no_of_days) \
			/ (days_in_year(get_datetime(first_date).year) * 100)

		make_loan_disbursement_entry(loan.name, loan.loan_amount, disbursement_date=first_date)
		process_loan_interest_accrual_for_demand_loans(posting_date = last_date)

		amounts = calculate_amounts(loan.name, add_days(last_date, 5))

		repayment_entry = create_repayment_entry(loan.name, self.applicant2, add_days(last_date, 5), flt(loan.loan_amount + accrued_interest_amount))
		repayment_entry.submit()

		amounts = frappe.db.get_value('Loan Interest Accrual', {'loan': loan.name}, ['paid_interest_amount',
			'paid_principal_amount'])

		request_loan_closure(loan.name)
		loan.load_from_db()
		self.assertEquals(loan.status, "Loan Closure Requested")

		amounts = calculate_amounts(loan.name, add_days(last_date, 5))
		self.assertEqual(amounts['pending_principal_amount'], 0.0)

	def test_partial_unaccrued_interest_payment(self):
		pledge = [{
			"loan_security": "Test Security 1",
			"qty": 4000.00
		}]

		loan_application = create_loan_application('_Test Company', self.applicant2, 'Demand Loan', pledge)
		create_pledge(loan_application)

		loan = create_demand_loan(self.applicant2, "Demand Loan", loan_application, posting_date='2019-10-01')
		loan.submit()

		self.assertEquals(loan.loan_amount, 1000000)

		first_date = '2019-10-01'
		last_date = '2019-10-30'

		no_of_days = date_diff(last_date, first_date) + 1

		no_of_days += 5.5

		# get partial unaccrued interest amount
		paid_amount = (loan.loan_amount * loan.rate_of_interest * no_of_days) \
			/ (days_in_year(get_datetime(first_date).year) * 100)

		make_loan_disbursement_entry(loan.name, loan.loan_amount, disbursement_date=first_date)
		process_loan_interest_accrual_for_demand_loans(posting_date = last_date)

		amounts = calculate_amounts(loan.name, add_days(last_date, 5))

		repayment_entry = create_repayment_entry(loan.name, self.applicant2, add_days(last_date, 5),
			paid_amount)

		repayment_entry.submit()
		repayment_entry.load_from_db()

		partial_accrued_interest_amount = (loan.loan_amount * loan.rate_of_interest * 5) \
			/ (days_in_year(get_datetime(first_date).year) * 100)

		interest_amount = flt(amounts['interest_amount'] + partial_accrued_interest_amount, 2)
		self.assertEqual(flt(repayment_entry.total_interest_paid, 0), flt(interest_amount, 0))

	def test_penalty(self):
		pledge = [{
			"loan_security": "Test Security 1",
			"qty": 4000.00
		}]

		loan_application = create_loan_application('_Test Company', self.applicant2, 'Demand Loan', pledge)
		create_pledge(loan_application)

		loan = create_demand_loan(self.applicant2, "Demand Loan", loan_application, posting_date='2019-10-01')
		loan.submit()

		self.assertEquals(loan.loan_amount, 1000000)

		first_date = '2019-10-01'
		last_date = '2019-10-30'

		make_loan_disbursement_entry(loan.name, loan.loan_amount, disbursement_date=first_date)
		process_loan_interest_accrual_for_demand_loans(posting_date = last_date)

		amounts = calculate_amounts(loan.name, add_days(last_date, 1))
		paid_amount = amounts['interest_amount']/2

		repayment_entry = create_repayment_entry(loan.name, self.applicant2, add_days(last_date, 5),
			paid_amount)

		repayment_entry.submit()

		# 30 days - grace period
		penalty_days = 30 - 4
		penalty_applicable_amount = flt(amounts['interest_amount']/2)
		penalty_amount = flt((((penalty_applicable_amount * 25) / 100) * penalty_days), 2)
		process = process_loan_interest_accrual_for_demand_loans(posting_date = '2019-11-30')

		calculated_penalty_amount = frappe.db.get_value('Loan Interest Accrual',
			{'process_loan_interest_accrual': process, 'loan': loan.name}, 'penalty_amount')

		self.assertEquals(calculated_penalty_amount, penalty_amount)

	def test_loan_write_off_limit(self):
		pledge = [{
			"loan_security": "Test Security 1",
			"qty": 4000.00
		}]

		loan_application = create_loan_application('_Test Company', self.applicant2, 'Demand Loan', pledge)
		create_pledge(loan_application)

		loan = create_demand_loan(self.applicant2, "Demand Loan", loan_application, posting_date='2019-10-01')
		loan.submit()

		self.assertEquals(loan.loan_amount, 1000000)

		first_date = '2019-10-01'
		last_date = '2019-10-30'

		no_of_days = date_diff(last_date, first_date) + 1
		no_of_days += 5

		accrued_interest_amount = (loan.loan_amount * loan.rate_of_interest * no_of_days) \
			/ (days_in_year(get_datetime(first_date).year) * 100)

		make_loan_disbursement_entry(loan.name, loan.loan_amount, disbursement_date=first_date)
		process_loan_interest_accrual_for_demand_loans(posting_date = last_date)

		# repay 50 less so that it can be automatically written off
		repayment_entry = create_repayment_entry(loan.name, self.applicant2, add_days(last_date, 5),
			flt(loan.loan_amount + accrued_interest_amount - 50))

		repayment_entry.submit()

		amount = frappe.db.get_value('Loan Interest Accrual', {'loan': loan.name}, ['sum(paid_interest_amount)'])

		self.assertEquals(flt(amount, 0),flt(accrued_interest_amount, 0))
		self.assertEquals(flt(repayment_entry.penalty_amount, 5), 0)

		amounts = calculate_amounts(loan.name, add_days(last_date, 5))
		self.assertEquals(flt(amounts['pending_principal_amount'], 0), 50)

		request_loan_closure(loan.name)
		loan.load_from_db()
		self.assertEquals(loan.status, "Loan Closure Requested")

	def test_loan_amount_write_off(self):
		pledge = [{
			"loan_security": "Test Security 1",
			"qty": 4000.00
		}]

		loan_application = create_loan_application('_Test Company', self.applicant2, 'Demand Loan', pledge)
		create_pledge(loan_application)

		loan = create_demand_loan(self.applicant2, "Demand Loan", loan_application, posting_date='2019-10-01')
		loan.submit()

		self.assertEquals(loan.loan_amount, 1000000)

		first_date = '2019-10-01'
		last_date = '2019-10-30'

		no_of_days = date_diff(last_date, first_date) + 1
		no_of_days += 5

		accrued_interest_amount = (loan.loan_amount * loan.rate_of_interest * no_of_days) \
			/ (days_in_year(get_datetime(first_date).year) * 100)

		make_loan_disbursement_entry(loan.name, loan.loan_amount, disbursement_date=first_date)
		process_loan_interest_accrual_for_demand_loans(posting_date = last_date)

		# repay 100 less so that it can be automatically written off
		repayment_entry = create_repayment_entry(loan.name, self.applicant2, add_days(last_date, 5),
			flt(loan.loan_amount + accrued_interest_amount - 100))

		repayment_entry.submit()

		amount = frappe.db.get_value('Loan Interest Accrual', {'loan': loan.name}, ['sum(paid_interest_amount)'])

		self.assertEquals(flt(amount, 0),flt(accrued_interest_amount, 0))
		self.assertEquals(flt(repayment_entry.penalty_amount, 5), 0)

		amounts = calculate_amounts(loan.name, add_days(last_date, 5))
		self.assertEquals(flt(amounts['pending_principal_amount'], 0), 100)

		we = make_loan_write_off(loan.name, amount=amounts['pending_principal_amount'])
		we.submit()

		amounts = calculate_amounts(loan.name, add_days(last_date, 5))
		self.assertEquals(flt(amounts['pending_principal_amount'], 0), 0)


def create_loan_accounts():
	if not frappe.db.exists("Account", "Loans and Advances (Assets) - _TC"):
		frappe.get_doc({
			"doctype": "Account",
			"account_name": "Loans and Advances (Assets)",
			"company": "_Test Company",
			"root_type": "Asset",
			"report_type": "Balance Sheet",
			"currency": "INR",
			"parent_account": "Current Assets - _TC",
			"account_type": "Bank",
			"is_group": 1
		}).insert(ignore_permissions=True)

	if not frappe.db.exists("Account", "Loan Account - _TC"):
		frappe.get_doc({
			"doctype": "Account",
			"company": "_Test Company",
			"account_name": "Loan Account",
			"root_type": "Asset",
			"report_type": "Balance Sheet",
			"currency": "INR",
			"parent_account": "Loans and Advances (Assets) - _TC",
			"account_type": "Bank",
		}).insert(ignore_permissions=True)

	if not frappe.db.exists("Account", "Payment Account - _TC"):
		frappe.get_doc({
			"doctype": "Account",
			"company": "_Test Company",
			"account_name": "Payment Account",
			"root_type": "Asset",
			"report_type": "Balance Sheet",
			"currency": "INR",
			"parent_account": "Bank Accounts - _TC",
			"account_type": "Bank",
		}).insert(ignore_permissions=True)

	if not frappe.db.exists("Account", "Interest Income Account - _TC"):
		frappe.get_doc({
			"doctype": "Account",
			"company": "_Test Company",
			"root_type": "Income",
			"account_name": "Interest Income Account",
			"report_type": "Profit and Loss",
			"currency": "INR",
			"parent_account": "Direct Income - _TC",
			"account_type": "Income Account",
		}).insert(ignore_permissions=True)

	if not frappe.db.exists("Account", "Penalty Income Account - _TC"):
		frappe.get_doc({
			"doctype": "Account",
			"company": "_Test Company",
			"account_name": "Penalty Income Account",
			"root_type": "Income",
			"report_type": "Profit and Loss",
			"currency": "INR",
			"parent_account": "Direct Income - _TC",
			"account_type": "Income Account",
		}).insert(ignore_permissions=True)

def create_loan_type(loan_name, maximum_loan_amount, rate_of_interest, penalty_interest_rate=None, is_term_loan=None, grace_period_in_days=None,
	mode_of_payment=None, payment_account=None, loan_account=None, interest_income_account=None, penalty_income_account=None,
	repayment_method=None, repayment_periods=None):

	if not frappe.db.exists("Loan Type", loan_name):
		loan_type = frappe.get_doc({
			"doctype": "Loan Type",
			"company": "_Test Company",
			"loan_name": loan_name,
			"is_term_loan": is_term_loan,
			"maximum_loan_amount": maximum_loan_amount,
			"rate_of_interest": rate_of_interest,
			"penalty_interest_rate": penalty_interest_rate,
			"grace_period_in_days": grace_period_in_days,
			"mode_of_payment": mode_of_payment,
			"payment_account": payment_account,
			"loan_account": loan_account,
			"interest_income_account": interest_income_account,
			"penalty_income_account": penalty_income_account,
			"repayment_method": repayment_method,
			"repayment_periods": repayment_periods,
			"write_off_amount": 100
		}).insert()

		loan_type.submit()

def create_loan_security_type():
	if not frappe.db.exists("Loan Security Type", "Stock"):
		frappe.get_doc({
			"doctype": "Loan Security Type",
			"loan_security_type": "Stock",
			"unit_of_measure": "Nos",
			"haircut": 50.00,
			"loan_to_value_ratio": 50
		}).insert(ignore_permissions=True)

def create_loan_security():
	if not frappe.db.exists("Loan Security", "Test Security 1"):
		frappe.get_doc({
			"doctype": "Loan Security",
			"loan_security_type": "Stock",
			"loan_security_code": "532779",
			"loan_security_name": "Test Security 1",
			"unit_of_measure": "Nos",
			"haircut": 50.00,
		}).insert(ignore_permissions=True)

	if not frappe.db.exists("Loan Security", "Test Security 2"):
		frappe.get_doc({
			"doctype": "Loan Security",
			"loan_security_type": "Stock",
			"loan_security_code": "531335",
			"loan_security_name": "Test Security 2",
			"unit_of_measure": "Nos",
			"haircut": 50.00,
		}).insert(ignore_permissions=True)

def create_loan_security_pledge(applicant, pledges, loan_application=None, loan=None):

	lsp = frappe.new_doc("Loan Security Pledge")
	lsp.applicant_type = 'Customer'
	lsp.applicant = applicant
	lsp.company = "_Test Company"
	lsp.loan_application = loan_application

	if loan:
		lsp.loan = loan

	for pledge in pledges:
		lsp.append('securities', {
			"loan_security": pledge['loan_security'],
			"qty": pledge['qty']
		})

	lsp.save()
	lsp.submit()

	return lsp

def make_loan_disbursement_entry(loan, amount, disbursement_date=None):

	loan_disbursement_entry = frappe.get_doc({
		"doctype": "Loan Disbursement",
		"against_loan": loan,
		"disbursement_date": disbursement_date,
		"company": "_Test Company",
		"disbursed_amount": amount,
		"cost_center": 'Main - _TC'
	}).insert(ignore_permissions=True)

	loan_disbursement_entry.save()
	loan_disbursement_entry.submit()

	return loan_disbursement_entry

def create_loan_security_price(loan_security, loan_security_price, uom, from_date, to_date):

	if not frappe.db.get_value("Loan Security Price",{"loan_security": loan_security,
		"valid_from": ("<=", from_date), "valid_upto": (">=", to_date)}, 'name'):

		lsp = frappe.get_doc({
			"doctype": "Loan Security Price",
			"loan_security": loan_security,
			"loan_security_price": loan_security_price,
			"uom": uom,
			"valid_from":from_date,
			"valid_upto": to_date
		}).insert(ignore_permissions=True)

def create_repayment_entry(loan, applicant, posting_date, paid_amount):

	lr = frappe.get_doc({
		"doctype": "Loan Repayment",
		"against_loan": loan,
		"company": "_Test Company",
		"posting_date": posting_date or nowdate(),
		"applicant": applicant,
		"amount_paid": paid_amount,
		"loan_type": "Stock Loan"
	}).insert(ignore_permissions=True)

	return lr

def create_loan_application(company, applicant, loan_type, proposed_pledges, repayment_method=None,
	repayment_periods=None, posting_date=None):
	loan_application = frappe.new_doc('Loan Application')
	loan_application.applicant_type = 'Customer'
	loan_application.company = company
	loan_application.applicant = applicant
	loan_application.loan_type = loan_type
	loan_application.posting_date = posting_date or nowdate()
	loan_application.is_secured_loan = 1

	if repayment_method:
		loan_application.repayment_method = repayment_method
		loan_application.repayment_periods = repayment_periods

	for pledge in proposed_pledges:
		loan_application.append('proposed_pledges', pledge)

	loan_application.save()
	loan_application.submit()

	loan_application.status = 'Approved'
	loan_application.save()

	return loan_application.name


def create_loan(applicant, loan_type, loan_amount, repayment_method, repayment_periods,
	repayment_start_date=None, posting_date=None):

	loan = frappe.get_doc({
		"doctype": "Loan",
		"applicant_type": "Employee",
		"company": "_Test Company",
		"applicant": applicant,
		"loan_type": loan_type,
		"loan_amount": loan_amount,
		"repayment_method": repayment_method,
		"repayment_periods": repayment_periods,
		"repayment_start_date": nowdate(),
		"is_term_loan": 1,
		"posting_date": posting_date or nowdate()
	})

	loan.save()
	return loan

def create_loan_with_security(applicant, loan_type, repayment_method, repayment_periods, loan_application, posting_date=None, repayment_start_date=None):
	loan = frappe.get_doc({
		"doctype": "Loan",
		"company": "_Test Company",
		"applicant_type": "Customer",
		"posting_date": posting_date or nowdate(),
		"loan_application": loan_application,
		"applicant": applicant,
		"loan_type": loan_type,
		"is_term_loan": 1,
		"is_secured_loan": 1,
		"repayment_method": repayment_method,
		"repayment_periods": repayment_periods,
		"repayment_start_date": repayment_start_date or nowdate(),
		"mode_of_payment": frappe.db.get_value('Mode of Payment', {'type': 'Cash'}, 'name'),
		"payment_account": 'Payment Account - _TC',
		"loan_account": 'Loan Account - _TC',
		"interest_income_account": 'Interest Income Account - _TC',
		"penalty_income_account": 'Penalty Income Account - _TC',
	})

	loan.save()

	return loan

def create_demand_loan(applicant, loan_type, loan_application, posting_date=None):

	loan = frappe.get_doc({
		"doctype": "Loan",
		"company": "_Test Company",
		"applicant_type": "Customer",
		"posting_date": posting_date or nowdate(),
		'loan_application': loan_application,
		"applicant": applicant,
		"loan_type": loan_type,
		"is_term_loan": 0,
		"is_secured_loan": 1,
		"mode_of_payment": frappe.db.get_value('Mode of Payment', {'type': 'Cash'}, 'name'),
		"payment_account": 'Payment Account - _TC',
		"loan_account": 'Loan Account - _TC',
		"interest_income_account": 'Interest Income Account - _TC',
		"penalty_income_account": 'Penalty Income Account - _TC',
	})

	loan.save()

	return loan