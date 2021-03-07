# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
import erpnext
from frappe.utils.make_random import get_random
from frappe.utils import nowdate, add_days, add_years, getdate, add_months
from erpnext.payroll.doctype.salary_structure.salary_structure import make_salary_slip
from erpnext.payroll.doctype.salary_slip.test_salary_slip import make_earning_salary_component,\
	make_deduction_salary_component, make_employee_salary_slip, create_tax_slab
from erpnext.hr.doctype.employee.test_employee import make_employee
from erpnext.payroll.doctype.employee_tax_exemption_declaration.test_employee_tax_exemption_declaration import create_payroll_period


test_dependencies = ["Fiscal Year"]

class TestSalaryStructure(unittest.TestCase):
	def setUp(self):
		for dt in ["Salary Slip", "Salary Structure", "Salary Structure Assignment"]:
			frappe.db.sql("delete from `tab%s`" % dt)

		self.make_holiday_list()
		frappe.db.set_value("Company", erpnext.get_default_company(), "default_holiday_list", "Salary Structure Test Holiday List")
		make_employee("test_employee@salary.com")
		make_employee("test_employee_2@salary.com")

	def make_holiday_list(self):
		if not frappe.db.get_value("Holiday List", "Salary Structure Test Holiday List"):
			holiday_list = frappe.get_doc({
				"doctype": "Holiday List",
				"holiday_list_name": "Salary Structure Test Holiday List",
				"from_date": nowdate(),
				"to_date": add_years(nowdate(), 1),
				"weekly_off": "Sunday"
			}).insert()
			holiday_list.get_weekly_off_dates()
			holiday_list.save()

	def test_salary_structure_deduction_based_on_gross_pay(self):

		emp = make_employee("test_employee_3@salary.com")

		sal_struct = make_salary_structure("Salary Structure 2", "Monthly", dont_submit = True)

		sal_struct.earnings = [sal_struct.earnings[0]]
		sal_struct.earnings[0].amount_based_on_formula = 1
		sal_struct.earnings[0].formula =  "base"

		sal_struct.deductions = [sal_struct.deductions[0]]

		sal_struct.deductions[0].amount_based_on_formula = 1
		sal_struct.deductions[0].condition = "gross_pay > 100"
		sal_struct.deductions[0].formula =  "gross_pay * 0.2"

		sal_struct.submit()

		assignment = create_salary_structure_assignment(emp, "Salary Structure 2")
		ss = make_salary_slip(sal_struct.name, employee = emp)

		self.assertEqual(assignment.base * 0.2, ss.deductions[0].amount)

	def test_amount_totals(self):
		frappe.db.set_value("Payroll Settings", None, "include_holidays_in_total_working_days", 0)
		sal_slip = frappe.get_value("Salary Slip", {"employee_name":"test_employee_2@salary.com"})
		if not sal_slip:
			sal_slip = make_employee_salary_slip("test_employee_2@salary.com", "Monthly", "Salary Structure Sample")
			self.assertEqual(sal_slip.get("salary_structure"), 'Salary Structure Sample')
			self.assertEqual(sal_slip.get("earnings")[0].amount, 50000)
			self.assertEqual(sal_slip.get("earnings")[1].amount, 3000)
			self.assertEqual(sal_slip.get("earnings")[2].amount, 25000)
			self.assertEqual(sal_slip.get("gross_pay"), 78000)
			self.assertEqual(sal_slip.get("deductions")[0].amount, 200)
			self.assertEqual(sal_slip.get("net_pay"), 78000 - sal_slip.get("total_deduction"))

	def test_whitespaces_in_formula_conditions_fields(self):
		salary_structure = make_salary_structure("Salary Structure Sample", "Monthly", dont_submit=True)

		for row in salary_structure.earnings:
			row.formula = "\n%s\n\n"%row.formula
			row.condition = "\n%s\n\n"%row.condition

		for row in salary_structure.deductions:
			row.formula = "\n%s\n\n"%row.formula
			row.condition = "\n%s\n\n"%row.condition

		salary_structure.save()

		for row in salary_structure.earnings:
			self.assertFalse("\n" in row.formula or "\n" in row.condition)

		for row in salary_structure.deductions:
			self.assertFalse(("\n" in row.formula) or ("\n" in row.condition))

	def test_salary_structures_assignment(self):
		company_currency = erpnext.get_default_currency()
		salary_structure = make_salary_structure("Salary Structure Sample", "Monthly", currency=company_currency)
		employee = "test_assign_stucture@salary.com"
		employee_doc_name = make_employee(employee)
		# clear the already assigned stuctures
		frappe.db.sql('''delete from `tabSalary Structure Assignment` where employee=%s and salary_structure=%s ''',
					  ("test_assign_stucture@salary.com",salary_structure.name))
		#test structure_assignment
		salary_structure.assign_salary_structure(employee=employee_doc_name,from_date='2013-01-01',base=5000,variable=200)
		salary_structure_assignment = frappe.get_doc("Salary Structure Assignment",{'employee':employee_doc_name, 'from_date':'2013-01-01'})
		self.assertEqual(salary_structure_assignment.docstatus, 1)
		self.assertEqual(salary_structure_assignment.base, 5000)
		self.assertEqual(salary_structure_assignment.variable, 200)

	def test_multi_currency_salary_structure(self):
		make_employee("test_muti_currency_employee@salary.com")
		sal_struct = make_salary_structure("Salary Structure Multi Currency", "Monthly", currency='USD')
		self.assertEqual(sal_struct.currency, 'USD')

def make_salary_structure(salary_structure, payroll_frequency, employee=None, dont_submit=False, other_details=None,
	test_tax=False, company=None, currency=erpnext.get_default_currency(), payroll_period=None):
	if test_tax:
		frappe.db.sql("""delete from `tabSalary Structure` where name=%s""",(salary_structure))

	if not frappe.db.exists('Salary Structure', salary_structure):
		details = {
			"doctype": "Salary Structure",
			"name": salary_structure,
			"company": company or erpnext.get_default_company(),
			"earnings": make_earning_salary_component(test_tax=test_tax, company_list=["_Test Company"]),
			"deductions": make_deduction_salary_component(test_tax=test_tax, company_list=["_Test Company"]),
			"payroll_frequency": payroll_frequency,
			"payment_account": get_random("Account", filters={'account_currency': currency}),
			"currency": currency
		}
		if other_details and isinstance(other_details, dict):
			details.update(other_details)
		salary_structure_doc = frappe.get_doc(details)
		salary_structure_doc.insert()
		if not dont_submit:
			salary_structure_doc.submit()

	else:
		salary_structure_doc = frappe.get_doc("Salary Structure", salary_structure)

	if employee and not frappe.db.get_value("Salary Structure Assignment",
		{'employee':employee, 'docstatus': 1}) and salary_structure_doc.docstatus==1:
			create_salary_structure_assignment(employee, salary_structure, company=company, currency=currency,
			payroll_period=payroll_period)

	return salary_structure_doc

def create_salary_structure_assignment(employee, salary_structure, from_date=None, company=None, currency=erpnext.get_default_currency(),
	payroll_period=None):

	if frappe.db.exists("Salary Structure Assignment", {"employee": employee}):
		frappe.db.sql("""delete from `tabSalary Structure Assignment` where employee=%s""",(employee))

	if not payroll_period:
		payroll_period = create_payroll_period()

	income_tax_slab = frappe.db.get_value("Income Tax Slab", {"currency": currency})

	if not income_tax_slab:
		income_tax_slab = create_tax_slab(payroll_period, allow_tax_exemption=True, currency=currency)

	salary_structure_assignment = frappe.new_doc("Salary Structure Assignment")
	salary_structure_assignment.employee = employee
	salary_structure_assignment.base = 50000
	salary_structure_assignment.variable = 5000
	salary_structure_assignment.from_date = from_date or add_days(nowdate(), -1)
	salary_structure_assignment.salary_structure = salary_structure
	salary_structure_assignment.currency = currency
	salary_structure_assignment.payroll_payable_account = get_payable_account(company)
	salary_structure_assignment.company = company or erpnext.get_default_company()
	salary_structure_assignment.save(ignore_permissions=True)
	salary_structure_assignment.income_tax_slab = income_tax_slab
	salary_structure_assignment.submit()
	return salary_structure_assignment

def get_payable_account(company=None):
	if not company:
		company = erpnext.get_default_company()
	return frappe.db.get_value("Company", company, "default_payroll_payable_account")