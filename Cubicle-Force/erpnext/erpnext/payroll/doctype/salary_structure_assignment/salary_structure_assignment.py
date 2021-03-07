# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate
from frappe.model.document import Document

class DuplicateAssignment(frappe.ValidationError): pass

class SalaryStructureAssignment(Document):
	def validate(self):
		self.validate_dates()
		self.validate_income_tax_slab()
		self.set_payroll_payable_account()

	def validate_dates(self):
		joining_date, relieving_date = frappe.db.get_value("Employee", self.employee,
			["date_of_joining", "relieving_date"])

		if self.from_date:
			if frappe.db.exists("Salary Structure Assignment", {"employee": self.employee, "from_date": self.from_date, "docstatus": 1}):
				frappe.throw(_("Salary Structure Assignment for Employee already exists"), DuplicateAssignment)

			if joining_date and getdate(self.from_date) < joining_date:
				frappe.throw(_("From Date {0} cannot be before employee's joining Date {1}")
					.format(self.from_date, joining_date))

			# flag - old_employee is for migrating the old employees data via patch
			if relieving_date and getdate(self.from_date) > relieving_date and not self.flags.old_employee:
				frappe.throw(_("From Date {0} cannot be after employee's relieving Date {1}")
					.format(self.from_date, relieving_date))

	def validate_income_tax_slab(self):
		if not self.income_tax_slab:
			return
		
		income_tax_slab_currency = frappe.db.get_value('Income Tax Slab', self.income_tax_slab, 'currency')
		if self.currency != income_tax_slab_currency:
			frappe.throw(_("Currency of selected Income Tax Slab should be {0} instead of {1}").format(self.currency, income_tax_slab_currency))

	def set_payroll_payable_account(self):
		if not self.payroll_payable_account:
			payroll_payable_account = frappe.db.get_value('Company', self.company, 'default_payroll_payable_account')
			if not payroll_payable_account:
				payroll_payable_account = frappe.db.get_value(
					"Account", {
						"account_name": _("Payroll Payable"), "company": self.company, "account_currency": frappe.db.get_value(
							"Company", self.company, "default_currency"), "is_group": 0})
			self.payroll_payable_account = payroll_payable_account

def get_assigned_salary_structure(employee, on_date):
	if not employee or not on_date:
		return None
	salary_structure = frappe.db.sql("""
		select salary_structure from `tabSalary Structure Assignment`
		where employee=%(employee)s
		and docstatus = 1
		and %(on_date)s >= from_date order by from_date desc limit 1""", {
			'employee': employee,
			'on_date': on_date,
		})
	return salary_structure[0][0] if salary_structure else None

@frappe.whitelist()
def get_employee_currency(employee):
	employee_currency = frappe.db.get_value('Salary Structure Assignment', {'employee': employee}, 'currency')
	if not employee_currency:
		frappe.throw(_("There is no Salary Structure assigned to {0}. First assign a Salary Stucture.").format(employee))
	return employee_currency