# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _, bold
from frappe.utils import getdate, date_diff, comma_and, formatdate, get_datetime, flt
from math import ceil
import json
from six import string_types

class LeavePolicyAssignment(Document):

	def validate(self):
		self.validate_policy_assignment_overlap()
		self.set_dates()

	def set_dates(self):
		if self.assignment_based_on == "Leave Period":
			self.effective_from, self.effective_to = frappe.db.get_value("Leave Period", self.leave_period, ["from_date", "to_date"])
		elif self.assignment_based_on == "Joining Date":
			self.effective_from = frappe.db.get_value("Employee", self.employee, "date_of_joining")

	def validate_policy_assignment_overlap(self):
		leave_policy_assignments = frappe.get_all("Leave Policy Assignment", filters = {
			"employee": self.employee,
			"name": ("!=", self.name),
			"docstatus": 1,
			"effective_to": (">=", self.effective_from),
			"effective_from": ("<=", self.effective_to)
		})

		if len(leave_policy_assignments):
			frappe.throw(_("Leave Policy: {0} already assigned for Employee {1} for period {2} to {3}")
				.format(bold(self.leave_policy), bold(self.employee), bold(formatdate(self.effective_from)), bold(formatdate(self.effective_to))))

	def grant_leave_alloc_for_employee(self):
		if self.leaves_allocated:
			frappe.throw(_("Leave already have been assigned for this Leave Policy Assignment"))
		else:
			leave_allocations = {}
			leave_type_details = get_leave_type_details()

			leave_policy = frappe.get_doc("Leave Policy", self.leave_policy)
			date_of_joining = frappe.db.get_value("Employee", self.employee, "date_of_joining")

			for leave_policy_detail in leave_policy.leave_policy_details:
				if not leave_type_details.get(leave_policy_detail.leave_type).is_lwp:
					leave_allocation, new_leaves_allocated = self.create_leave_allocation(
						leave_policy_detail.leave_type, leave_policy_detail.annual_allocation,
						leave_type_details, date_of_joining
					)

				leave_allocations[leave_policy_detail.leave_type] = {"name": leave_allocation, "leaves": new_leaves_allocated}

			self.db_set("leaves_allocated", 1)
			return leave_allocations

	def create_leave_allocation(self, leave_type, new_leaves_allocated, leave_type_details, date_of_joining):
		# Creates leave allocation for the given employee in the provided leave period
		carry_forward = self.carry_forward
		if self.carry_forward and not leave_type_details.get(leave_type).is_carry_forward:
			carry_forward = 0

		new_leaves_allocated = self.get_new_leaves(leave_type, new_leaves_allocated,
			leave_type_details, date_of_joining)

		allocation = frappe.get_doc(dict(
			doctype="Leave Allocation",
			employee=self.employee,
			leave_type=leave_type,
			from_date=self.effective_from,
			to_date=self.effective_to,
			new_leaves_allocated=new_leaves_allocated,
			leave_period=self.leave_period or None,
			leave_policy_assignment = self.name,
			leave_policy = self.leave_policy,
			carry_forward=carry_forward
			))
		allocation.save(ignore_permissions = True)
		allocation.submit()
		return allocation.name, new_leaves_allocated

	def get_new_leaves(self, leave_type, new_leaves_allocated, leave_type_details, date_of_joining):
		from frappe.model.meta import get_field_precision
		precision = get_field_precision(frappe.get_meta("Leave Allocation").get_field("new_leaves_allocated"))

		# Earned Leaves and Compensatory Leaves are allocated by scheduler, initially allocate 0
		if leave_type_details.get(leave_type).is_compensatory == 1:
			new_leaves_allocated = 0

		elif leave_type_details.get(leave_type).is_earned_leave == 1:
			if self.assignment_based_on == "Leave Period":
				new_leaves_allocated = self.get_leaves_for_passed_months(leave_type, new_leaves_allocated, leave_type_details, date_of_joining)
			else:
				new_leaves_allocated = 0
		# Calculate leaves at pro-rata basis for employees joining after the beginning of the given leave period
		elif getdate(date_of_joining) > getdate(self.effective_from):
			remaining_period = ((date_diff(self.effective_to, date_of_joining) + 1) / (date_diff(self.effective_to, self.effective_from) + 1))
			new_leaves_allocated = ceil(new_leaves_allocated * remaining_period)

		return flt(new_leaves_allocated, precision)

	def get_leaves_for_passed_months(self, leave_type, new_leaves_allocated, leave_type_details, date_of_joining):
		from erpnext.hr.utils import get_monthly_earned_leave

		current_month = get_datetime().month
		current_year = get_datetime().year

		from_date = frappe.db.get_value("Leave Period", self.leave_period, "from_date")
		if getdate(date_of_joining) > getdate(from_date):
			from_date = date_of_joining

		from_date_month = get_datetime(from_date).month
		from_date_year = get_datetime(from_date).year

		months_passed = 0
		if current_year == from_date_year and current_month > from_date_month:
			months_passed = current_month - from_date_month
		elif current_year > from_date_year:
			months_passed = (12 - from_date_month) + current_month

		if months_passed > 0:
			monthly_earned_leave = get_monthly_earned_leave(new_leaves_allocated,
				leave_type_details.get(leave_type).earned_leave_frequency, leave_type_details.get(leave_type).rounding)
			new_leaves_allocated = monthly_earned_leave * months_passed

		return new_leaves_allocated


@frappe.whitelist()
def grant_leave_for_multiple_employees(leave_policy_assignments):
	leave_policy_assignments = json.loads(leave_policy_assignments)
	not_granted = []
	for assignment in leave_policy_assignments:
		try:
			frappe.get_doc("Leave Policy Assignment", assignment).grant_leave_alloc_for_employee()
		except Exception:
			not_granted.append(assignment)

		if len(not_granted):
			msg = _("Leave not Granted for Assignments:")+ bold(comma_and(not_granted)) + _(". Please Check documents")
		else:
			msg = _("Leave granted Successfully")
	frappe.msgprint(msg)

@frappe.whitelist()
def create_assignment_for_multiple_employees(employees, data):

	if isinstance(employees, string_types):
		employees= json.loads(employees)

	if isinstance(data, string_types):
		data = frappe._dict(json.loads(data))

	docs_name = []
	for employee in employees:
		assignment = frappe.new_doc("Leave Policy Assignment")
		assignment.employee = employee
		assignment.assignment_based_on = data.assignment_based_on or None
		assignment.leave_policy = data.leave_policy
		assignment.effective_from = getdate(data.effective_from) or None
		assignment.effective_to = getdate(data.effective_to) or None
		assignment.leave_period = data.leave_period or None
		assignment.carry_forward = data.carry_forward

		assignment.save()
		assignment.submit()
		docs_name.append(assignment.name)
	return docs_name


def automatically_allocate_leaves_based_on_leave_policy():
	today = getdate()
	automatically_allocate_leaves_based_on_leave_policy = frappe.db.get_single_value(
		'HR Settings', 'automatically_allocate_leaves_based_on_leave_policy'
	)

	pending_assignments = frappe.get_list(
		"Leave Policy Assignment",
		filters = {"docstatus": 1, "leaves_allocated": 0, "effective_from": today}
	)

	if len(pending_assignments) and automatically_allocate_leaves_based_on_leave_policy:
		for assignment in pending_assignments:
			frappe.get_doc("Leave Policy Assignment", assignment.name).grant_leave_alloc_for_employee()


def get_leave_type_details():
	leave_type_details = frappe._dict()
	leave_types = frappe.get_all("Leave Type",
		fields=["name", "is_lwp", "is_earned_leave", "is_compensatory",
			"is_carry_forward", "expire_carry_forwarded_leaves_after_days", "earned_leave_frequency", "rounding"])
	for d in leave_types:
		leave_type_details.setdefault(d.name, d)
	return leave_type_details

