from __future__ import unicode_literals
import frappe, erpnext
import random
import datetime
from frappe.utils import random_string, add_days, get_last_day, getdate
from erpnext.projects.doctype.timesheet.test_timesheet import make_timesheet
from erpnext.projects.doctype.timesheet.timesheet import make_salary_slip, make_sales_invoice
from frappe.utils.make_random import get_random
from erpnext.hr.doctype.expense_claim.test_expense_claim import get_payable_account
from erpnext.hr.doctype.expense_claim.expense_claim import make_bank_entry
from erpnext.hr.doctype.leave_application.leave_application import (get_leave_balance_on,
	OverlapError, AttendanceAlreadyMarkedError)

def work():
	frappe.set_user(frappe.db.get_global('demo_hr_user'))
	year, month = frappe.flags.current_date.strftime("%Y-%m").split("-")
	setup_department_approvers()
	mark_attendance()
	make_leave_application()

	# payroll entry
	if not frappe.db.sql('select name from `tabSalary Slip` where month(adddate(start_date, interval 1 month))=month(curdate())'):
		# based on frequency
		payroll_entry = get_payroll_entry()
		payroll_entry.salary_slip_based_on_timesheet = 0
		payroll_entry.save()
		payroll_entry.create_salary_slips()
		payroll_entry.submit_salary_slips()
		payroll_entry.make_accrual_jv_entry()
		payroll_entry.submit()
		# payroll_entry.make_journal_entry(reference_date=frappe.flags.current_date,
		# 	reference_number=random_string(10))

		# based on timesheet
		payroll_entry = get_payroll_entry()
		payroll_entry.salary_slip_based_on_timesheet = 1
		payroll_entry.save()
		payroll_entry.create_salary_slips()
		payroll_entry.submit_salary_slips()
		payroll_entry.make_accrual_jv_entry()
		payroll_entry.submit()
		# payroll_entry.make_journal_entry(reference_date=frappe.flags.current_date,
		# 	reference_number=random_string(10))

	if frappe.db.get_global('demo_hr_user'):
		make_timesheet_records()

		#expense claim
		expense_claim = frappe.new_doc("Expense Claim")
		expense_claim.extend('expenses', get_expenses())
		expense_claim.employee = get_random("Employee")
		expense_claim.company = frappe.flags.company
		expense_claim.payable_account = get_payable_account(expense_claim.company)
		expense_claim.posting_date = frappe.flags.current_date
		expense_claim.expense_approver = frappe.db.get_global('demo_hr_user')
		expense_claim.save()

		rand = random.random()

		if rand < 0.4:
			update_sanctioned_amount(expense_claim)
			expense_claim.approval_status = 'Approved'
			expense_claim.submit()

			if random.randint(0, 1):
				#make journal entry against expense claim
				je = frappe.get_doc(make_bank_entry("Expense Claim", expense_claim.name))
				je.posting_date = frappe.flags.current_date
				je.cheque_no = random_string(10)
				je.cheque_date = frappe.flags.current_date
				je.flags.ignore_permissions = 1
				je.submit()

def get_payroll_entry():
	# process payroll for previous month
	payroll_entry = frappe.new_doc("Payroll Entry")
	payroll_entry.company = frappe.flags.company
	payroll_entry.payroll_frequency = 'Monthly'

	# select a posting date from the previous month
	payroll_entry.posting_date = get_last_day(getdate(frappe.flags.current_date) - datetime.timedelta(days=10))
	payroll_entry.payment_account = frappe.get_value('Account', {'account_type': 'Cash', 'company': erpnext.get_default_company(),'is_group':0}, "name")

	payroll_entry.set_start_end_dates()
	return payroll_entry

def get_expenses():
	expenses = []
	expese_types = frappe.db.sql("""select ect.name, eca.default_account from `tabExpense Claim Type` ect,
		`tabExpense Claim Account` eca where eca.parent=ect.name
		and eca.company=%s """, frappe.flags.company,as_dict=1)

	for expense_type in expese_types[:random.randint(1,4)]:
		claim_amount = random.randint(1,20)*10

		expenses.append({
			"expense_date": frappe.flags.current_date,
			"expense_type": expense_type.name,
			"default_account": expense_type.default_account or "Miscellaneous Expenses - WPL",
			"amount": claim_amount,
			"sanctioned_amount": claim_amount
		})

	return expenses

def update_sanctioned_amount(expense_claim):
	for expense in expense_claim.expenses:
		sanctioned_amount = random.randint(1,20)*10

		if sanctioned_amount < expense.amount:
			expense.sanctioned_amount = sanctioned_amount

def get_timesheet_based_salary_slip_employee():
	sal_struct = frappe.db.sql("""
			select name from `tabSalary Structure`
			where salary_slip_based_on_timesheet = 1
			and docstatus != 2""")
	if sal_struct:
		employees = frappe.db.sql("""
				select employee from `tabSalary Structure Assignment`
				where salary_structure IN %(sal_struct)s""", {"sal_struct": sal_struct}, as_dict=True)
		return employees
	else:
		return []

def make_timesheet_records():
	employees = get_timesheet_based_salary_slip_employee()
	for e in employees:
		ts = make_timesheet(e.employee, simulate = True, billable = 1, activity_type=get_random("Activity Type"), company=frappe.flags.company)
		frappe.db.commit()

		rand = random.random()
		if rand >= 0.3:
			make_salary_slip_for_timesheet(ts.name)

		rand = random.random()
		if rand >= 0.2:
			make_sales_invoice_for_timesheet(ts.name)

def make_salary_slip_for_timesheet(name):
	salary_slip = make_salary_slip(name)
	salary_slip.insert()
	salary_slip.submit()
	frappe.db.commit()

def make_sales_invoice_for_timesheet(name):
	sales_invoice = make_sales_invoice(name)
	sales_invoice.customer = get_random("Customer")
	sales_invoice.append('items', {
		'item_code': get_random("Item", {"has_variants": 0, "is_stock_item": 0,
			"is_fixed_asset": 0}),
		'qty': 1,
		'rate': 1000
	})
	sales_invoice.flags.ignore_permissions = 1
	sales_invoice.set_missing_values()
	sales_invoice.calculate_taxes_and_totals()
	sales_invoice.insert()
	sales_invoice.submit()
	frappe.db.commit()

def make_leave_application():
	allocated_leaves = frappe.get_all("Leave Allocation", fields=['employee', 'leave_type'])

	for allocated_leave in allocated_leaves:
		leave_balance = get_leave_balance_on(allocated_leave.employee, allocated_leave.leave_type, frappe.flags.current_date,
			consider_all_leaves_in_the_allocation_period=True)
		if leave_balance != 0:
			if leave_balance == 1:
				to_date = frappe.flags.current_date
			else:
				to_date = add_days(frappe.flags.current_date, random.randint(0, leave_balance-1))

			leave_application = frappe.get_doc({
				"doctype": "Leave Application",
				"employee": allocated_leave.employee,
				"from_date": frappe.flags.current_date,
				"to_date": to_date,
				"leave_type": allocated_leave.leave_type,
			})
			try:
				leave_application.insert()
				leave_application.submit()
				frappe.db.commit()
			except (OverlapError, AttendanceAlreadyMarkedError):
				frappe.db.rollback()

def mark_attendance():
	attendance_date = frappe.flags.current_date
	for employee in frappe.get_all('Employee', fields=['name'], filters = {'status': 'Active'}):

		if not frappe.db.get_value("Attendance", {"employee": employee.name, "attendance_date": attendance_date}):
			attendance = frappe.get_doc({
				"doctype": "Attendance",
				"employee": employee.name,
				"attendance_date": attendance_date
			})

			leave = frappe.db.sql("""select name from `tabLeave Application`
				where employee = %s and %s between from_date and to_date
				and docstatus = 1""", (employee.name, attendance_date))

			if leave:
				attendance.status = "Absent"
			else:
				attendance.status = "Present"
			attendance.save()
			attendance.submit()
			frappe.db.commit()

def setup_department_approvers():
	for d in frappe.get_all('Department', filters={'department_name': ['!=', 'All Departments']}):
		doc = frappe.get_doc('Department', d.name)
		doc.append("leave_approvers", {'approver': frappe.session.user})
		doc.append("expense_approvers", {'approver': frappe.session.user})
		doc.flags.ignore_mandatory = True
		doc.save()
