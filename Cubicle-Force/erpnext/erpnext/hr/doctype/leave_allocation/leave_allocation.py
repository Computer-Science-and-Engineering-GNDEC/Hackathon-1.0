# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, date_diff, formatdate, add_days, today, getdate
from frappe import _
from frappe.model.document import Document
from erpnext.hr.utils import set_employee_name, get_leave_period
from erpnext.hr.doctype.leave_ledger_entry.leave_ledger_entry import expire_allocation, create_leave_ledger_entry

class OverlapError(frappe.ValidationError): pass
class BackDatedAllocationError(frappe.ValidationError): pass
class OverAllocationError(frappe.ValidationError): pass
class LessAllocationError(frappe.ValidationError): pass
class ValueMultiplierError(frappe.ValidationError): pass

class LeaveAllocation(Document):
	def validate(self):
		self.validate_period()
		self.validate_allocation_overlap()
		self.validate_back_dated_allocation()
		self.set_total_leaves_allocated()
		self.validate_total_leaves_allocated()
		self.validate_lwp()
		set_employee_name(self)
		self.validate_leave_allocation_days()

	def validate_leave_allocation_days(self):
		company = frappe.db.get_value("Employee", self.employee, "company")
		leave_period = get_leave_period(self.from_date, self.to_date, company)
		max_leaves_allowed = flt(frappe.db.get_value("Leave Type", self.leave_type, "max_leaves_allowed"))
		if max_leaves_allowed > 0:
			leave_allocated = 0
			if leave_period:
				leave_allocated = get_leave_allocation_for_period(self.employee, self.leave_type,
					leave_period[0].from_date, leave_period[0].to_date)
			leave_allocated += flt(self.new_leaves_allocated)
			if leave_allocated > max_leaves_allowed:
				frappe.throw(_("Total allocated leaves are more days than maximum allocation of {0} leave type for employee {1} in the period")
					.format(self.leave_type, self.employee))

	def on_submit(self):
		self.create_leave_ledger_entry()

		# expire all unused leaves in the ledger on creation of carry forward allocation
		allocation = get_previous_allocation(self.from_date, self.leave_type, self.employee)
		if self.carry_forward and allocation:
			expire_allocation(allocation)

	def on_cancel(self):
		self.create_leave_ledger_entry(submit=False)
		if self.leave_policy_assignment:
			self.update_leave_policy_assignments_when_no_allocations_left()
		if self.carry_forward:
			self.set_carry_forwarded_leaves_in_previous_allocation(on_cancel=True)

	def update_leave_policy_assignments_when_no_allocations_left(self):
		allocations = frappe.db.get_list("Leave Allocation", filters = {
			"docstatus": 1,
			"leave_policy_assignment": self.leave_policy_assignment
		})
		if len(allocations) == 0:
			frappe.db.set_value("Leave Policy Assignment", self.leave_policy_assignment ,"leaves_allocated", 0)

	def validate_period(self):
		if date_diff(self.to_date, self.from_date) <= 0:
			frappe.throw(_("To date cannot be before from date"))

	def validate_lwp(self):
		if frappe.db.get_value("Leave Type", self.leave_type, "is_lwp"):
			frappe.throw(_("Leave Type {0} cannot be allocated since it is leave without pay").format(self.leave_type))

	def validate_allocation_overlap(self):
		leave_allocation = frappe.db.sql("""
			SELECT
				name
			FROM `tabLeave Allocation`
			WHERE
				employee=%s AND leave_type=%s
				AND name <> %s AND docstatus=1
				AND to_date >= %s AND from_date <= %s""",
			(self.employee, self.leave_type, self.name, self.from_date, self.to_date))

		if leave_allocation:
			frappe.msgprint(_("{0} already allocated for Employee {1} for period {2} to {3}")
				.format(self.leave_type, self.employee, formatdate(self.from_date), formatdate(self.to_date)))

			frappe.throw(_('Reference') + ': <a href="/app/Form/Leave Allocation/{0}">{0}</a>'
				.format(leave_allocation[0][0]), OverlapError)

	def validate_back_dated_allocation(self):
		future_allocation = frappe.db.sql("""select name, from_date from `tabLeave Allocation`
			where employee=%s and leave_type=%s and docstatus=1 and from_date > %s
			and carry_forward=1""", (self.employee, self.leave_type, self.to_date), as_dict=1)

		if future_allocation:
			frappe.throw(_("Leave cannot be allocated before {0}, as leave balance has already been carry-forwarded in the future leave allocation record {1}")
				.format(formatdate(future_allocation[0].from_date), future_allocation[0].name),
					BackDatedAllocationError)

	def set_total_leaves_allocated(self):
		self.unused_leaves = get_carry_forwarded_leaves(self.employee,
			self.leave_type, self.from_date, self.carry_forward)

		self.total_leaves_allocated = flt(self.unused_leaves) + flt(self.new_leaves_allocated)

		self.limit_carry_forward_based_on_max_allowed_leaves()

		if self.carry_forward:
			self.set_carry_forwarded_leaves_in_previous_allocation()

		if not self.total_leaves_allocated \
			and not frappe.db.get_value("Leave Type", self.leave_type, "is_earned_leave") \
			and not frappe.db.get_value("Leave Type", self.leave_type, "is_compensatory"):
				frappe.throw(_("Total leaves allocated is mandatory for Leave Type {0}")
					.format(self.leave_type))

	def limit_carry_forward_based_on_max_allowed_leaves(self):
		max_leaves_allowed = frappe.db.get_value("Leave Type", self.leave_type, "max_leaves_allowed")
		if max_leaves_allowed and self.total_leaves_allocated > flt(max_leaves_allowed):
			self.total_leaves_allocated = flt(max_leaves_allowed)
			self.unused_leaves = max_leaves_allowed - flt(self.new_leaves_allocated)

	def set_carry_forwarded_leaves_in_previous_allocation(self, on_cancel=False):
		''' Set carry forwarded leaves in previous allocation '''
		previous_allocation = get_previous_allocation(self.from_date, self.leave_type, self.employee)
		if on_cancel:
			self.unused_leaves = 0.0
		if previous_allocation:
			frappe.db.set_value("Leave Allocation", previous_allocation.name,
				'carry_forwarded_leaves_count', self.unused_leaves)

	def validate_total_leaves_allocated(self):
		# Adding a day to include To Date in the difference
		date_difference = date_diff(self.to_date, self.from_date) + 1
		if date_difference < self.total_leaves_allocated:
			frappe.throw(_("Total allocated leaves are more than days in the period"), OverAllocationError)

	def create_leave_ledger_entry(self, submit=True):
		if self.unused_leaves:
			expiry_days = frappe.db.get_value("Leave Type", self.leave_type, "expire_carry_forwarded_leaves_after_days")
			end_date = add_days(self.from_date, expiry_days - 1) if expiry_days else self.to_date
			args = dict(
				leaves=self.unused_leaves,
				from_date=self.from_date,
				to_date= min(getdate(end_date), getdate(self.to_date)),
				is_carry_forward=1
			)
			create_leave_ledger_entry(self, args, submit)

		args = dict(
			leaves=self.new_leaves_allocated,
			from_date=self.from_date,
			to_date=self.to_date,
			is_carry_forward=0
		)
		create_leave_ledger_entry(self, args, submit)

def get_previous_allocation(from_date, leave_type, employee):
	''' Returns document properties of previous allocation '''
	return frappe.db.get_value("Leave Allocation",
		filters={
			'to_date': ("<", from_date),
			'leave_type': leave_type,
			'employee': employee,
			'docstatus': 1
		},
		order_by='to_date DESC',
		fieldname=['name', 'from_date', 'to_date', 'employee', 'leave_type'], as_dict=1)

def get_leave_allocation_for_period(employee, leave_type, from_date, to_date):
	leave_allocated = 0
	leave_allocations = frappe.db.sql("""
		select employee, leave_type, from_date, to_date, total_leaves_allocated
		from `tabLeave Allocation`
		where employee=%(employee)s and leave_type=%(leave_type)s
			and docstatus=1
			and (from_date between %(from_date)s and %(to_date)s
				or to_date between %(from_date)s and %(to_date)s
				or (from_date < %(from_date)s and to_date > %(to_date)s))
	""", {
		"from_date": from_date,
		"to_date": to_date,
		"employee": employee,
		"leave_type": leave_type
	}, as_dict=1)

	if leave_allocations:
		for leave_alloc in leave_allocations:
			leave_allocated += leave_alloc.total_leaves_allocated

	return leave_allocated

@frappe.whitelist()
def get_carry_forwarded_leaves(employee, leave_type, date, carry_forward=None):
	''' Returns carry forwarded leaves for the given employee '''
	unused_leaves = 0.0
	previous_allocation = get_previous_allocation(date, leave_type, employee)
	if carry_forward and previous_allocation:
		validate_carry_forward(leave_type)
		unused_leaves = get_unused_leaves(employee, leave_type,
			previous_allocation.from_date, previous_allocation.to_date)
		if unused_leaves:
			max_carry_forwarded_leaves = frappe.db.get_value("Leave Type",
				leave_type, "maximum_carry_forwarded_leaves")
			if max_carry_forwarded_leaves and unused_leaves > flt(max_carry_forwarded_leaves):
				unused_leaves = flt(max_carry_forwarded_leaves)

	return unused_leaves

def get_unused_leaves(employee, leave_type, from_date, to_date):
	''' Returns unused leaves between the given period while skipping leave allocation expiry '''
	leaves = frappe.get_all("Leave Ledger Entry", filters={
		'employee': employee,
		'leave_type': leave_type,
		'from_date': ('>=', from_date),
		'to_date': ('<=', to_date)
		}, or_filters={
			'is_expired': 0,
			'is_carry_forward': 1
		}, fields=['sum(leaves) as leaves'])
	return flt(leaves[0]['leaves'])

def validate_carry_forward(leave_type):
	if not frappe.db.get_value("Leave Type", leave_type, "is_carry_forward"):
		frappe.throw(_("Leave Type {0} cannot be carry-forwarded").format(leave_type))