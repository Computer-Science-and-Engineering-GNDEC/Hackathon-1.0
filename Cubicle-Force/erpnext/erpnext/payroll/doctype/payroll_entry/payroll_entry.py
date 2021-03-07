# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe.model.document import Document
from dateutil.relativedelta import relativedelta
from frappe.utils import cint, flt, add_days, getdate, add_to_date, DATE_FORMAT, date_diff, comma_and
from frappe import _
from erpnext.accounts.utils import get_fiscal_year
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee

class PayrollEntry(Document):
	def onload(self):
		if not self.docstatus==1 or self.salary_slips_submitted:
    			return

		# check if salary slips were manually submitted
		entries = frappe.db.count("Salary Slip", {'payroll_entry': self.name, 'docstatus': 1}, ['name'])
		if cint(entries) == len(self.employees):
				self.set_onload("submitted_ss", True)

	def validate(self):
		self.number_of_employees = len(self.employees)

	def on_submit(self):
		self.create_salary_slips()

	def before_submit(self):
		self.validate_employee_details()
		if self.validate_attendance:
			if self.validate_employee_attendance():
				frappe.throw(_("Cannot Submit, Employees left to mark attendance"))

	def validate_employee_details(self):
		emp_with_sal_slip = []
		for employee_details in self.employees:
			if frappe.db.exists("Salary Slip", {"employee": employee_details.employee, "start_date": self.start_date, "end_date": self.end_date, "docstatus": 1}):
				emp_with_sal_slip.append(employee_details.employee)

		if len(emp_with_sal_slip):
			frappe.throw(_("Salary Slip already exists for {0} ").format(comma_and(emp_with_sal_slip)))

	def on_cancel(self):
		frappe.delete_doc("Salary Slip", frappe.db.sql_list("""select name from `tabSalary Slip`
			where payroll_entry=%s """, (self.name)))

	def get_emp_list(self):
		"""
			Returns list of active employees based on selected criteria
			and for which salary structure exists
		"""
		cond = self.get_filter_condition()
		cond += self.get_joining_relieving_condition()

		condition = ''
		if self.payroll_frequency:
			condition = """and payroll_frequency = '%(payroll_frequency)s'"""% {"payroll_frequency": self.payroll_frequency}

		sal_struct = frappe.db.sql_list("""
				select
					name from `tabSalary Structure`
				where
					docstatus = 1 and
					is_active = 'Yes'
					and company = %(company)s
					and currency = %(currency)s and
					ifnull(salary_slip_based_on_timesheet,0) = %(salary_slip_based_on_timesheet)s
					{condition}""".format(condition=condition),
				{"company": self.company, "currency": self.currency, "salary_slip_based_on_timesheet":self.salary_slip_based_on_timesheet})

		if sal_struct:
			cond += "and t2.salary_structure IN %(sal_struct)s "
			cond += "and t2.payroll_payable_account = %(payroll_payable_account)s "
			cond += "and %(from_date)s >= t2.from_date"
			emp_list = frappe.db.sql("""
				select
					distinct t1.name as employee, t1.employee_name, t1.department, t1.designation
				from
					`tabEmployee` t1, `tabSalary Structure Assignment` t2
				where
					t1.name = t2.employee
					and t2.docstatus = 1
			%s order by t2.from_date desc
			""" % cond, {"sal_struct": tuple(sal_struct), "from_date": self.end_date, "payroll_payable_account": self.payroll_payable_account}, as_dict=True)

			emp_list = self.remove_payrolled_employees(emp_list)
			return emp_list

	def remove_payrolled_employees(self, emp_list):
		for employee_details in emp_list:
			if frappe.db.exists("Salary Slip", {"employee": employee_details.employee, "start_date": self.start_date, "end_date": self.end_date, "docstatus": 1}):
				emp_list.remove(employee_details)

		return emp_list

	def fill_employee_details(self):
		self.set('employees', [])
		employees = self.get_emp_list()
		if not employees:
			error_msg = _("No employees found for the mentioned criteria:<br>Company: {0}<br> Currency: {1}<br>Payroll Payable Account: {2}").format(
				frappe.bold(self.company), frappe.bold(self.currency), frappe.bold(self.payroll_payable_account))
			if self.branch:
				error_msg += "<br>" + _("Branch: {0}").format(frappe.bold(self.branch))
			if self.department:
				error_msg += "<br>" + _("Department: {0}").format(frappe.bold(self.department))
			if self.designation:
				error_msg += "<br>" + _("Designation: {0}").format(frappe.bold(self.designation))
			if self.start_date:
				error_msg += "<br>" + _("Start date: {0}").format(frappe.bold(self.start_date))
			if self.end_date:
				error_msg += "<br>" + _("End date: {0}").format(frappe.bold(self.end_date))
			frappe.throw(error_msg, title=_("No employees found"))

		for d in employees:
			self.append('employees', d)

		self.number_of_employees = len(self.employees)
		if self.validate_attendance:
			return self.validate_employee_attendance()

	def get_filter_condition(self):
		self.check_mandatory()

		cond = ''
		for f in ['company', 'branch', 'department', 'designation']:
			if self.get(f):
				cond += " and t1." + f + " = " + frappe.db.escape(self.get(f))

		return cond

	def get_joining_relieving_condition(self):
		cond = """
			and ifnull(t1.date_of_joining, '0000-00-00') <= '%(end_date)s'
			and ifnull(t1.relieving_date, '2199-12-31') >= '%(start_date)s'
		""" % {"start_date": self.start_date, "end_date": self.end_date}
		return cond

	def check_mandatory(self):
		for fieldname in ['company', 'start_date', 'end_date']:
			if not self.get(fieldname):
				frappe.throw(_("Please set {0}").format(self.meta.get_label(fieldname)))

	def create_salary_slips(self):
		"""
			Creates salary slip for selected employees if already not created
		"""
		self.check_permission('write')
		self.created = 1
		employees = [emp.employee for emp in self.employees]
		if employees:
			args = frappe._dict({
				"salary_slip_based_on_timesheet": self.salary_slip_based_on_timesheet,
				"payroll_frequency": self.payroll_frequency,
				"start_date": self.start_date,
				"end_date": self.end_date,
				"company": self.company,
				"posting_date": self.posting_date,
				"deduct_tax_for_unclaimed_employee_benefits": self.deduct_tax_for_unclaimed_employee_benefits,
				"deduct_tax_for_unsubmitted_tax_exemption_proof": self.deduct_tax_for_unsubmitted_tax_exemption_proof,
				"payroll_entry": self.name,
				"exchange_rate": self.exchange_rate,
				"currency": self.currency
			})
			if len(employees) > 30:
				frappe.enqueue(create_salary_slips_for_employees, timeout=600, employees=employees, args=args)
			else:
				create_salary_slips_for_employees(employees, args, publish_progress=False)
				# since this method is called via frm.call this doc needs to be updated manually
				self.reload()

	def get_sal_slip_list(self, ss_status, as_dict=False):
		"""
			Returns list of salary slips based on selected criteria
		"""
		cond = self.get_filter_condition()

		ss_list = frappe.db.sql("""
			select t1.name, t1.salary_structure, t1.payroll_cost_center from `tabSalary Slip` t1
			where t1.docstatus = %s and t1.start_date >= %s and t1.end_date <= %s
			and (t1.journal_entry is null or t1.journal_entry = "") and ifnull(salary_slip_based_on_timesheet,0) = %s %s
		""" % ('%s', '%s', '%s','%s', cond), (ss_status, self.start_date, self.end_date, self.salary_slip_based_on_timesheet), as_dict=as_dict)
		return ss_list

	def submit_salary_slips(self):
		self.check_permission('write')
		ss_list = self.get_sal_slip_list(ss_status=0)
		if len(ss_list) > 30:
			frappe.enqueue(submit_salary_slips_for_employees, timeout=600, payroll_entry=self, salary_slips=ss_list)
		else:
			submit_salary_slips_for_employees(self, ss_list, publish_progress=False)

	def email_salary_slip(self, submitted_ss):
		if frappe.db.get_single_value("Payroll Settings", "email_salary_slip_to_employee"):
			for ss in submitted_ss:
				ss.email_salary_slip()

	def get_salary_component_account(self, salary_component):
		account = frappe.db.get_value("Salary Component Account",
			{"parent": salary_component, "company": self.company}, "account")

		if not account:
			frappe.throw(_("Please set account in Salary Component {0}")
				.format(salary_component))

		return account

	def get_salary_components(self, component_type):
		salary_slips = self.get_sal_slip_list(ss_status = 1, as_dict = True)
		if salary_slips:
			salary_components = frappe.db.sql("""
				select ssd.salary_component, ssd.amount, ssd.parentfield, ss.payroll_cost_center
				from `tabSalary Slip` ss, `tabSalary Detail` ssd
				where ss.name = ssd.parent and ssd.parentfield = '%s' and ss.name in (%s)
			""" % (component_type, ', '.join(['%s']*len(salary_slips))),
				tuple([d.name for d in salary_slips]), as_dict=True)

			return salary_components

	def get_salary_component_total(self, component_type = None):
		salary_components = self.get_salary_components(component_type)
		if salary_components:
			component_dict = {}
			for item in salary_components:
				add_component_to_accrual_jv_entry = True
				if component_type == "earnings":
					is_flexible_benefit, only_tax_impact = frappe.db.get_value("Salary Component", item['salary_component'], ['is_flexible_benefit', 'only_tax_impact'])
					if is_flexible_benefit == 1 and only_tax_impact ==1:
						add_component_to_accrual_jv_entry = False
				if add_component_to_accrual_jv_entry:
					component_dict[(item.salary_component, item.payroll_cost_center)] \
						= component_dict.get((item.salary_component, item.payroll_cost_center), 0) + flt(item.amount)
			account_details = self.get_account(component_dict = component_dict)
			return account_details

	def get_account(self, component_dict = None):
		account_dict = {}
		for key, amount in component_dict.items():
			account = self.get_salary_component_account(key[0])
			account_dict[(account, key[1])] = account_dict.get((account, key[1]), 0) + amount
		return account_dict

	def make_accrual_jv_entry(self):
		self.check_permission('write')
		earnings = self.get_salary_component_total(component_type = "earnings") or {}
		deductions = self.get_salary_component_total(component_type = "deductions") or {}
		payroll_payable_account = self.payroll_payable_account
		jv_name = ""
		precision = frappe.get_precision("Journal Entry Account", "debit_in_account_currency")

		if earnings or deductions:
			journal_entry = frappe.new_doc('Journal Entry')
			journal_entry.voucher_type = 'Journal Entry'
			journal_entry.user_remark = _('Accrual Journal Entry for salaries from {0} to {1}')\
				.format(self.start_date, self.end_date)
			journal_entry.company = self.company
			journal_entry.posting_date = self.posting_date

			accounts = []
			currencies = []
			payable_amount = 0
			multi_currency = 0
			company_currency = erpnext.get_company_currency(self.company)

			# Earnings
			for acc_cc, amount in earnings.items():
				exchange_rate, amt = self.get_amount_and_exchange_rate_for_journal_entry(acc_cc[0], amount, company_currency, currencies)
				payable_amount += flt(amount, precision)
				accounts.append({
						"account": acc_cc[0],
						"debit_in_account_currency": flt(amt, precision),
						"exchange_rate": flt(exchange_rate),
						"party_type": '',
						"cost_center": acc_cc[1] or self.cost_center,
						"project": self.project
					})

			# Deductions
			for acc_cc, amount in deductions.items():
				exchange_rate, amt = self.get_amount_and_exchange_rate_for_journal_entry(acc_cc[0], amount, company_currency, currencies)
				payable_amount -= flt(amount, precision)
				accounts.append({
						"account": acc_cc[0],
						"credit_in_account_currency": flt(amt, precision),
						"exchange_rate": flt(exchange_rate),
						"cost_center": acc_cc[1] or self.cost_center,
						"party_type": '',
						"project": self.project
					})

			# Payable amount
			exchange_rate, payable_amt = self.get_amount_and_exchange_rate_for_journal_entry(payroll_payable_account, payable_amount, company_currency, currencies)
			accounts.append({
				"account": payroll_payable_account,
				"credit_in_account_currency": flt(payable_amt, precision),
				"exchange_rate": flt(exchange_rate),
				"party_type": '',
				"cost_center": self.cost_center
			})

			journal_entry.set("accounts", accounts)
			if len(currencies) > 1:
				multi_currency = 1
			journal_entry.multi_currency = multi_currency
			journal_entry.title = payroll_payable_account
			journal_entry.save()

			try:
				journal_entry.submit()
				jv_name = journal_entry.name
				self.update_salary_slip_status(jv_name = jv_name)
			except Exception as e:
				if type(e) in (str, list, tuple):
					frappe.msgprint(e)
				raise

		return jv_name

	def get_amount_and_exchange_rate_for_journal_entry(self, account, amount, company_currency, currencies):
		conversion_rate = 1
		exchange_rate = self.exchange_rate
		account_currency = frappe.db.get_value('Account', account, 'account_currency')
		if account_currency not in currencies:
			currencies.append(account_currency)
		if account_currency == company_currency:
			conversion_rate = self.exchange_rate
			exchange_rate = 1
		amount = flt(amount) * flt(conversion_rate)
		return exchange_rate, amount

	def make_payment_entry(self):
		self.check_permission('write')

		cond = self.get_filter_condition()
		salary_slip_name_list = frappe.db.sql(""" select t1.name from `tabSalary Slip` t1
			where t1.docstatus = 1 and start_date >= %s and end_date <= %s %s
			""" % ('%s', '%s', cond), (self.start_date, self.end_date), as_list = True)

		if salary_slip_name_list and len(salary_slip_name_list) > 0:
			salary_slip_total = 0
			for salary_slip_name in salary_slip_name_list:
				salary_slip = frappe.get_doc("Salary Slip", salary_slip_name[0])
				for sal_detail in salary_slip.earnings:
					is_flexible_benefit, only_tax_impact, creat_separate_je, statistical_component = frappe.db.get_value("Salary Component", sal_detail.salary_component,
						['is_flexible_benefit', 'only_tax_impact', 'create_separate_payment_entry_against_benefit_claim', 'statistical_component'])
					if only_tax_impact != 1 and statistical_component != 1:
						if is_flexible_benefit == 1 and creat_separate_je == 1:
							self.create_journal_entry(sal_detail.amount, sal_detail.salary_component)
						else:
							salary_slip_total += sal_detail.amount
				for sal_detail in salary_slip.deductions:
					statistical_component = frappe.db.get_value("Salary Component", sal_detail.salary_component, 'statistical_component')
					if statistical_component != 1:
						salary_slip_total -= sal_detail.amount
			if salary_slip_total > 0:
				self.create_journal_entry(salary_slip_total, "salary")

	def create_journal_entry(self, je_payment_amount, user_remark):
		payroll_payable_account = self.payroll_payable_account
		precision = frappe.get_precision("Journal Entry Account", "debit_in_account_currency")

		accounts = []
		currencies = []
		multi_currency = 0
		company_currency = erpnext.get_company_currency(self.company)

		exchange_rate, amount = self.get_amount_and_exchange_rate_for_journal_entry(self.payment_account, je_payment_amount, company_currency, currencies)
		accounts.append({
				"account": self.payment_account,
				"bank_account": self.bank_account,
				"credit_in_account_currency": flt(amount, precision),
				"exchange_rate": flt(exchange_rate),
			})

		exchange_rate, amount = self.get_amount_and_exchange_rate_for_journal_entry(payroll_payable_account, je_payment_amount, company_currency, currencies)
		accounts.append({
				"account": payroll_payable_account,
				"debit_in_account_currency": flt(amount, precision),
				"exchange_rate": flt(exchange_rate),
				"reference_type": self.doctype,
				"reference_name": self.name
			})

		if len(currencies) > 1:
				multi_currency = 1

		journal_entry = frappe.new_doc('Journal Entry')
		journal_entry.voucher_type = 'Bank Entry'
		journal_entry.user_remark = _('Payment of {0} from {1} to {2}')\
			.format(user_remark, self.start_date, self.end_date)
		journal_entry.company = self.company
		journal_entry.posting_date = self.posting_date
		journal_entry.multi_currency = multi_currency

		journal_entry.set("accounts", accounts)
		journal_entry.save(ignore_permissions = True)

	def update_salary_slip_status(self, jv_name = None):
		ss_list = self.get_sal_slip_list(ss_status=1)
		for ss in ss_list:
			ss_obj = frappe.get_doc("Salary Slip",ss[0])
			frappe.db.set_value("Salary Slip", ss_obj.name, "journal_entry", jv_name)

	def set_start_end_dates(self):
		self.update(get_start_end_dates(self.payroll_frequency,
			self.start_date or self.posting_date, self.company))

	def validate_employee_attendance(self):
		employees_to_mark_attendance = []
		days_in_payroll, days_holiday, days_attendance_marked = 0, 0, 0
		for employee_detail in self.employees:
			employee_joining_date = frappe.db.get_value("Employee", employee_detail.employee, 'date_of_joining')
			start_date = self.start_date
			if employee_joining_date > getdate(self.start_date):
				start_date = employee_joining_date
			days_holiday = self.get_count_holidays_of_employee(employee_detail.employee, start_date)
			days_attendance_marked = self.get_count_employee_attendance(employee_detail.employee, start_date)
			days_in_payroll = date_diff(self.end_date, start_date) + 1
			if days_in_payroll > days_holiday + days_attendance_marked:
				employees_to_mark_attendance.append({
					"employee": employee_detail.employee,
					"employee_name": employee_detail.employee_name
					})
		return employees_to_mark_attendance

	def get_count_holidays_of_employee(self, employee, start_date):
		holiday_list = get_holiday_list_for_employee(employee)
		holidays = 0
		if holiday_list:
			days = frappe.db.sql("""select count(*) from tabHoliday where
				parent=%s and holiday_date between %s and %s""", (holiday_list,
				start_date, self.end_date))
			if days and days[0][0]:
				holidays = days[0][0]
		return holidays

	def get_count_employee_attendance(self, employee, start_date):
		marked_days = 0
		attendances = frappe.get_all("Attendance",
				fields = ["count(*)"],
				filters = {
					"employee": employee,
					"attendance_date": ('between', [start_date, self.end_date])
				}, as_list=1)
		if attendances and attendances[0][0]:
			marked_days = attendances[0][0]
		return marked_days

@frappe.whitelist()
def get_start_end_dates(payroll_frequency, start_date=None, company=None):
	'''Returns dict of start and end dates for given payroll frequency based on start_date'''

	if payroll_frequency == "Monthly" or payroll_frequency == "Bimonthly" or payroll_frequency == "":
		fiscal_year = get_fiscal_year(start_date, company=company)[0]
		month = "%02d" % getdate(start_date).month
		m = get_month_details(fiscal_year, month)
		if payroll_frequency == "Bimonthly":
			if getdate(start_date).day <= 15:
				start_date = m['month_start_date']
				end_date = m['month_mid_end_date']
			else:
				start_date = m['month_mid_start_date']
				end_date = m['month_end_date']
		else:
			start_date = m['month_start_date']
			end_date = m['month_end_date']

	if payroll_frequency == "Weekly":
		end_date = add_days(start_date, 6)

	if payroll_frequency == "Fortnightly":
		end_date = add_days(start_date, 13)

	if payroll_frequency == "Daily":
		end_date = start_date

	return frappe._dict({
		'start_date': start_date, 'end_date': end_date
	})

def get_frequency_kwargs(frequency_name):
	frequency_dict = {
		'monthly': {'months': 1},
		'fortnightly': {'days': 14},
		'weekly': {'days': 7},
		'daily': {'days': 1}
	}
	return frequency_dict.get(frequency_name)


@frappe.whitelist()
def get_end_date(start_date, frequency):
	start_date = getdate(start_date)
	frequency = frequency.lower() if frequency else 'monthly'
	kwargs = get_frequency_kwargs(frequency) if frequency != 'bimonthly' else get_frequency_kwargs('monthly')

	# weekly, fortnightly and daily intervals have fixed days so no problems
	end_date = add_to_date(start_date, **kwargs) - relativedelta(days=1)
	if frequency != 'bimonthly':
		return dict(end_date=end_date.strftime(DATE_FORMAT))

	else:
		return dict(end_date='')


def get_month_details(year, month):
	ysd = frappe.db.get_value("Fiscal Year", year, "year_start_date")
	if ysd:
		import calendar, datetime
		diff_mnt = cint(month)-cint(ysd.month)
		if diff_mnt<0:
			diff_mnt = 12-int(ysd.month)+cint(month)
		msd = ysd + relativedelta(months=diff_mnt) # month start date
		month_days = cint(calendar.monthrange(cint(msd.year) ,cint(month))[1]) # days in month
		mid_start = datetime.date(msd.year, cint(month), 16) # month mid start date
		mid_end = datetime.date(msd.year, cint(month), 15) # month mid end date
		med = datetime.date(msd.year, cint(month), month_days) # month end date
		return frappe._dict({
			'year': msd.year,
			'month_start_date': msd,
			'month_end_date': med,
			'month_mid_start_date': mid_start,
			'month_mid_end_date': mid_end,
			'month_days': month_days
		})
	else:
		frappe.throw(_("Fiscal Year {0} not found").format(year))

def get_payroll_entry_bank_entries(payroll_entry_name):
	journal_entries = frappe.db.sql(
		'select name from `tabJournal Entry Account` '
		'where reference_type="Payroll Entry" '
		'and reference_name=%s and docstatus=1',
		payroll_entry_name,
		as_dict=1
	)

	return journal_entries


@frappe.whitelist()
def payroll_entry_has_bank_entries(name):
	response = {}
	bank_entries = get_payroll_entry_bank_entries(name)
	response['submitted'] = 1 if bank_entries else 0

	return response

def create_salary_slips_for_employees(employees, args, publish_progress=True):
	salary_slips_exists_for = get_existing_salary_slips(employees, args)
	count=0
	for emp in employees:
		if emp not in salary_slips_exists_for:
			args.update({
				"doctype": "Salary Slip",
				"employee": emp
			})
			ss = frappe.get_doc(args)
			ss.insert()
			count+=1
			if publish_progress:
				frappe.publish_progress(count*100/len(set(employees) - set(salary_slips_exists_for)),
					title = _("Creating Salary Slips..."))
		else:
			salary_slip_name = frappe.db.sql(
				'''SELECT
						name
					FROM `tabSalary Slip`
					WHERE company=%s
					AND start_date >= %s
					AND end_date <= %s
					AND employee = %s
				''', (args.company, args.start_date, args.end_date, emp), as_dict=True)

			salary_slip_doc = frappe.get_doc('Salary Slip', salary_slip_name[0].name)
			salary_slip_doc.exchange_rate = args.exchange_rate
			salary_slip_doc.set_totals()
			salary_slip_doc.db_update()

	payroll_entry = frappe.get_doc("Payroll Entry", args.payroll_entry)
	payroll_entry.db_set("salary_slips_created", 1)
	payroll_entry.notify_update()

def get_existing_salary_slips(employees, args):
	return frappe.db.sql_list("""
		select distinct employee from `tabSalary Slip`
		where docstatus!= 2 and company = %s
			and start_date >= %s and end_date <= %s
			and employee in (%s)
	""" % ('%s', '%s', '%s', ', '.join(['%s']*len(employees))),
		[args.company, args.start_date, args.end_date] + employees)

def submit_salary_slips_for_employees(payroll_entry, salary_slips, publish_progress=True):
	submitted_ss = []
	not_submitted_ss = []
	frappe.flags.via_payroll_entry = True

	count = 0
	for ss in salary_slips:
		ss_obj = frappe.get_doc("Salary Slip",ss[0])
		if ss_obj.net_pay<0:
			not_submitted_ss.append(ss[0])
		else:
			try:
				ss_obj.submit()
				submitted_ss.append(ss_obj)
			except frappe.ValidationError:
				not_submitted_ss.append(ss[0])

		count += 1
		if publish_progress:
			frappe.publish_progress(count*100/len(salary_slips), title = _("Submitting Salary Slips..."))
	if submitted_ss:
		payroll_entry.make_accrual_jv_entry()
		frappe.msgprint(_("Salary Slip submitted for period from {0} to {1}")
			.format(ss_obj.start_date, ss_obj.end_date))

		payroll_entry.email_salary_slip(submitted_ss)

		payroll_entry.db_set("salary_slips_submitted", 1)
		payroll_entry.notify_update()

	if not submitted_ss and not not_submitted_ss:
		frappe.msgprint(_("No salary slip found to submit for the above selected criteria OR salary slip already submitted"))

	if not_submitted_ss:
		frappe.msgprint(_("Could not submit some Salary Slips"))

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_payroll_entries_for_jv(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""
		select name from `tabPayroll Entry`
		where `{key}` LIKE %(txt)s
		and name not in
			(select reference_name from `tabJournal Entry Account`
				where reference_type="Payroll Entry")
		order by name limit %(start)s, %(page_len)s"""
		.format(key=searchfield), {
			'txt': "%%%s%%" % frappe.db.escape(txt),
			'start': start, 'page_len': page_len
		})
