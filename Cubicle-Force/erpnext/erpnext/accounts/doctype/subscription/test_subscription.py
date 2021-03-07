# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt
from __future__ import unicode_literals

import unittest

import frappe
from erpnext.accounts.doctype.subscription.subscription import get_prorata_factor
from frappe.utils.data import (nowdate, add_days, add_to_date, add_months, date_diff, flt, get_date_str,
	get_first_day, get_last_day)

def create_plan():
	if not frappe.db.exists('Subscription Plan', '_Test Plan Name'):
		plan = frappe.new_doc('Subscription Plan')
		plan.plan_name = '_Test Plan Name'
		plan.item = '_Test Non Stock Item'
		plan.price_determination = "Fixed Rate"
		plan.cost = 900
		plan.billing_interval = 'Month'
		plan.billing_interval_count = 1
		plan.insert()

	if not frappe.db.exists('Subscription Plan', '_Test Plan Name 2'):
		plan = frappe.new_doc('Subscription Plan')
		plan.plan_name = '_Test Plan Name 2'
		plan.item = '_Test Non Stock Item'
		plan.price_determination = "Fixed Rate"
		plan.cost = 1999
		plan.billing_interval = 'Month'
		plan.billing_interval_count = 1
		plan.insert()

	if not frappe.db.exists('Subscription Plan', '_Test Plan Name 3'):
		plan = frappe.new_doc('Subscription Plan')
		plan.plan_name = '_Test Plan Name 3'
		plan.item = '_Test Non Stock Item'
		plan.price_determination = "Fixed Rate"
		plan.cost = 1999
		plan.billing_interval = 'Day'
		plan.billing_interval_count = 14
		plan.insert()

	# Defined a quarterly Subscription Plan
	if not frappe.db.exists('Subscription Plan', '_Test Plan Name 4'):
		plan = frappe.new_doc('Subscription Plan')
		plan.plan_name = '_Test Plan Name 4'
		plan.item = '_Test Non Stock Item'
		plan.price_determination = "Monthly Rate"
		plan.cost = 20000
		plan.billing_interval = 'Month'
		plan.billing_interval_count = 3
		plan.insert()

	if not frappe.db.exists('Supplier', '_Test Supplier'):
		supplier = frappe.new_doc('Supplier')
		supplier.supplier_name = '_Test Supplier'
		supplier.supplier_group = 'All Supplier Groups'
		supplier.insert()

class TestSubscription(unittest.TestCase):

	def setUp(self):
		create_plan()

	def test_create_subscription_with_trial_with_correct_period(self):
		subscription = frappe.new_doc('Subscription')
		subscription.party_type = 'Customer'
		subscription.party = '_Test Customer'
		subscription.trial_period_start = nowdate()
		subscription.trial_period_end = add_months(nowdate(), 1)
		subscription.append('plans', {'plan': '_Test Plan Name', 'qty': 1})
		subscription.save()

		self.assertEqual(subscription.trial_period_start, nowdate())
		self.assertEqual(subscription.trial_period_end, add_months(nowdate(), 1))
		self.assertEqual(add_days(subscription.trial_period_end, 1), get_date_str(subscription.current_invoice_start))
		self.assertEqual(add_to_date(subscription.current_invoice_start, months=1, days=-1), get_date_str(subscription.current_invoice_end))
		self.assertEqual(subscription.invoices, [])
		self.assertEqual(subscription.status, 'Trialling')

		subscription.delete()

	def test_create_subscription_without_trial_with_correct_period(self):
		subscription = frappe.new_doc('Subscription')
		subscription.party_type = 'Customer'
		subscription.party = '_Test Customer'
		subscription.append('plans', {'plan': '_Test Plan Name', 'qty': 1})
		subscription.save()

		self.assertEqual(subscription.trial_period_start, None)
		self.assertEqual(subscription.trial_period_end, None)
		self.assertEqual(subscription.current_invoice_start, nowdate())
		self.assertEqual(subscription.current_invoice_end, add_to_date(nowdate(), months=1, days=-1))
		# No invoice is created
		self.assertEqual(len(subscription.invoices), 0)
		self.assertEqual(subscription.status, 'Active')

		subscription.delete()

	def test_create_subscription_trial_with_wrong_dates(self):
		subscription = frappe.new_doc('Subscription')
		subscription.party_type = 'Customer'
		subscription.party = '_Test Customer'
		subscription.trial_period_end = nowdate()
		subscription.trial_period_start = add_days(nowdate(), 30)
		subscription.append('plans', {'plan': '_Test Plan Name', 'qty': 1})

		self.assertRaises(frappe.ValidationError, subscription.save)
		subscription.delete()

	def test_create_subscription_multi_with_different_billing_fails(self):
		subscription = frappe.new_doc('Subscription')
		subscription.party_type = 'Customer'
		subscription.party = '_Test Customer'
		subscription.trial_period_end = nowdate()
		subscription.trial_period_start = add_days(nowdate(), 30)
		subscription.append('plans', {'plan': '_Test Plan Name', 'qty': 1})
		subscription.append('plans', {'plan': '_Test Plan Name 3', 'qty': 1})

		self.assertRaises(frappe.ValidationError, subscription.save)
		subscription.delete()

	def test_invoice_is_generated_at_end_of_billing_period(self):
		subscription = frappe.new_doc('Subscription')
		subscription.party_type = 'Customer'
		subscription.party = '_Test Customer'
		subscription.start_date = '2018-01-01'
		subscription.append('plans', {'plan': '_Test Plan Name', 'qty': 1})
		subscription.insert()

		self.assertEqual(subscription.status, 'Active')
		self.assertEqual(subscription.current_invoice_start, '2018-01-01')
		self.assertEqual(subscription.current_invoice_end, '2018-01-31')
		subscription.process()

		self.assertEqual(len(subscription.invoices), 1)
		self.assertEqual(subscription.current_invoice_start, '2018-01-01')
		subscription.process()
		self.assertEqual(subscription.status, 'Unpaid')
		subscription.delete()

	def test_status_goes_back_to_active_after_invoice_is_paid(self):
		subscription = frappe.new_doc('Subscription')
		subscription.party_type = 'Customer'
		subscription.party = '_Test Customer'
		subscription.append('plans', {'plan': '_Test Plan Name', 'qty': 1})
		subscription.start_date = '2018-01-01'
		subscription.insert()
		subscription.process()	# generate first invoice
		self.assertEqual(len(subscription.invoices), 1)

		# Status is unpaid as Days until Due is zero and grace period is Zero
		self.assertEqual(subscription.status, 'Unpaid')

		subscription.get_current_invoice()
		current_invoice = subscription.get_current_invoice()

		self.assertIsNotNone(current_invoice)

		current_invoice.db_set('outstanding_amount', 0)
		current_invoice.db_set('status', 'Paid')
		subscription.process()

		self.assertEqual(subscription.status, 'Active')
		self.assertEqual(subscription.current_invoice_start, add_months(subscription.start_date, 1))
		self.assertEqual(len(subscription.invoices), 1)

		subscription.delete()

	def test_subscription_cancel_after_grace_period(self):
		settings = frappe.get_single('Subscription Settings')
		default_grace_period_action = settings.cancel_after_grace
		settings.cancel_after_grace = 1
		settings.save()

		subscription = frappe.new_doc('Subscription')
		subscription.party_type = 'Customer'
		subscription.party = '_Test Customer'
		subscription.append('plans', {'plan': '_Test Plan Name', 'qty': 1})
		subscription.start_date = '2018-01-01'
		subscription.insert()

		self.assertEqual(subscription.status, 'Active')

		subscription.process()		# generate first invoice
		# This should change status to Cancelled since grace period is 0
		# And is backdated subscription so subscription will be cancelled after processing
		self.assertEqual(subscription.status, 'Cancelled')

		settings.cancel_after_grace = default_grace_period_action
		settings.save()
		subscription.delete()

	def test_subscription_unpaid_after_grace_period(self):
		settings = frappe.get_single('Subscription Settings')
		default_grace_period_action = settings.cancel_after_grace
		settings.cancel_after_grace = 0
		settings.save()

		subscription = frappe.new_doc('Subscription')
		subscription.party_type = 'Customer'
		subscription.party = '_Test Customer'
		subscription.append('plans', {'plan': '_Test Plan Name', 'qty': 1})
		subscription.start_date = '2018-01-01'
		subscription.insert()
		subscription.process()		# generate first invoice

		# Status is unpaid as Days until Due is zero and grace period is Zero
		self.assertEqual(subscription.status, 'Unpaid')

		settings.cancel_after_grace = default_grace_period_action
		settings.save()
		subscription.delete()

	def test_subscription_invoice_days_until_due(self):
		subscription = frappe.new_doc('Subscription')
		subscription.party_type = 'Customer'
		subscription.party = '_Test Customer'
		subscription.append('plans', {'plan': '_Test Plan Name', 'qty': 1})
		subscription.days_until_due = 10
		subscription.start_date = add_months(nowdate(), -1)
		subscription.insert()
		subscription.process()		# generate first invoice
		self.assertEqual(len(subscription.invoices), 1)
		self.assertEqual(subscription.status, 'Active')

		subscription.delete()

	def test_subscription_is_past_due_doesnt_change_within_grace_period(self):
		settings = frappe.get_single('Subscription Settings')
		grace_period = settings.grace_period
		settings.grace_period = 1000
		settings.save()

		subscription = frappe.new_doc('Subscription')
		subscription.party_type = 'Customer'
		subscription.party = '_Test Customer'
		subscription.append('plans', {'plan': '_Test Plan Name', 'qty': 1})
		subscription.start_date = add_days(nowdate(), -1000)
		subscription.insert()
		subscription.process()		# generate first invoice

		self.assertEqual(subscription.status, 'Past Due Date')

		subscription.process()
		# Grace period is 1000 days so status should remain as Past Due Date
		self.assertEqual(subscription.status, 'Past Due Date')

		subscription.process()
		self.assertEqual(subscription.status, 'Past Due Date')

		subscription.process()
		self.assertEqual(subscription.status, 'Past Due Date')

		settings.grace_period = grace_period
		settings.save()
		subscription.delete()

	def test_subscription_remains_active_during_invoice_period(self):
		subscription = frappe.new_doc('Subscription')
		subscription.party_type = 'Customer'
		subscription.party = '_Test Customer'
		subscription.append('plans', {'plan': '_Test Plan Name', 'qty': 1})
		subscription.save()
		subscription.process()		# no changes expected

		self.assertEqual(subscription.status, 'Active')
		self.assertEqual(subscription.current_invoice_start, nowdate())
		self.assertEqual(subscription.current_invoice_end, add_to_date(nowdate(), months=1, days=-1))
		self.assertEqual(len(subscription.invoices), 0)

		subscription.process()		# no changes expected still
		self.assertEqual(subscription.status, 'Active')
		self.assertEqual(subscription.current_invoice_start, nowdate())
		self.assertEqual(subscription.current_invoice_end, add_to_date(nowdate(), months=1, days=-1))
		self.assertEqual(len(subscription.invoices), 0)

		subscription.process()		# no changes expected yet still
		self.assertEqual(subscription.status, 'Active')
		self.assertEqual(subscription.current_invoice_start, nowdate())
		self.assertEqual(subscription.current_invoice_end, add_to_date(nowdate(), months=1, days=-1))
		self.assertEqual(len(subscription.invoices), 0)

		subscription.delete()

	def test_subscription_cancelation(self):
		subscription = frappe.new_doc('Subscription')
		subscription.party_type = 'Customer'
		subscription.party = '_Test Customer'
		subscription.append('plans', {'plan': '_Test Plan Name', 'qty': 1})
		subscription.save()
		subscription.cancel_subscription()

		self.assertEqual(subscription.status, 'Cancelled')

		subscription.delete()

	def test_subscription_cancellation_invoices(self):
		settings = frappe.get_single('Subscription Settings')
		to_prorate = settings.prorate
		settings.prorate = 1
		settings.save()

		subscription = frappe.new_doc('Subscription')
		subscription.party_type = 'Customer'
		subscription.party = '_Test Customer'
		subscription.append('plans', {'plan': '_Test Plan Name', 'qty': 1})
		subscription.save()

		self.assertEqual(subscription.status, 'Active')

		subscription.cancel_subscription()
		# Invoice must have been generated
		self.assertEqual(len(subscription.invoices), 1)

		invoice = subscription.get_current_invoice()
		diff = flt(date_diff(nowdate(), subscription.current_invoice_start) + 1)
		plan_days = flt(date_diff(subscription.current_invoice_end, subscription.current_invoice_start) + 1)
		prorate_factor = flt(diff/plan_days)

		self.assertEqual(
			flt(
				get_prorata_factor(subscription.current_invoice_end, subscription.current_invoice_start,
					subscription.generate_invoice_at_period_start),
				2),
			flt(prorate_factor, 2)
		)
		self.assertEqual(flt(invoice.grand_total, 2), flt(prorate_factor * 900, 2))
		self.assertEqual(subscription.status, 'Cancelled')

		subscription.delete()
		settings.prorate = to_prorate
		settings.save()

	def test_subscription_cancellation_invoices_with_prorata_false(self):
		settings = frappe.get_single('Subscription Settings')
		to_prorate = settings.prorate
		settings.prorate = 0
		settings.save()

		subscription = frappe.new_doc('Subscription')
		subscription.party_type = 'Customer'
		subscription.party = '_Test Customer'
		subscription.append('plans', {'plan': '_Test Plan Name', 'qty': 1})
		subscription.save()
		subscription.cancel_subscription()
		invoice = subscription.get_current_invoice()

		self.assertEqual(invoice.grand_total, 900)

		settings.prorate = to_prorate
		settings.save()

		subscription.delete()

	def test_subscription_cancellation_invoices_with_prorata_true(self):
		settings = frappe.get_single('Subscription Settings')
		to_prorate = settings.prorate
		settings.prorate = 1
		settings.save()

		subscription = frappe.new_doc('Subscription')
		subscription.party_type = 'Customer'
		subscription.party = '_Test Customer'
		subscription.append('plans', {'plan': '_Test Plan Name', 'qty': 1})
		subscription.save()
		subscription.cancel_subscription()

		invoice = subscription.get_current_invoice()
		diff = flt(date_diff(nowdate(), subscription.current_invoice_start) + 1)
		plan_days = flt(date_diff(subscription.current_invoice_end, subscription.current_invoice_start) + 1)
		prorate_factor = flt(diff / plan_days)

		self.assertEqual(flt(invoice.grand_total, 2), flt(prorate_factor * 900, 2))

		settings.prorate = to_prorate
		settings.save()

		subscription.delete()

	def test_subcription_cancellation_and_process(self):
		settings = frappe.get_single('Subscription Settings')
		default_grace_period_action = settings.cancel_after_grace
		settings.cancel_after_grace = 1
		settings.save()

		subscription = frappe.new_doc('Subscription')
		subscription.party_type = 'Customer'
		subscription.party = '_Test Customer'
		subscription.append('plans', {'plan': '_Test Plan Name', 'qty': 1})
		subscription.start_date = '2018-01-01'
		subscription.insert()
		subscription.process()	# generate first invoice
		invoices = len(subscription.invoices)

		subscription.cancel_subscription()
		self.assertEqual(subscription.status, 'Cancelled')
		self.assertEqual(len(subscription.invoices), invoices)

		subscription.process()
		self.assertEqual(subscription.status, 'Cancelled')
		self.assertEqual(len(subscription.invoices), invoices)

		subscription.process()
		self.assertEqual(subscription.status, 'Cancelled')
		self.assertEqual(len(subscription.invoices), invoices)

		settings.cancel_after_grace = default_grace_period_action
		settings.save()
		subscription.delete()

	def test_subscription_restart_and_process(self):
		settings = frappe.get_single('Subscription Settings')
		default_grace_period_action = settings.cancel_after_grace
		settings.grace_period = 0
		settings.cancel_after_grace = 0
		settings.save()

		subscription = frappe.new_doc('Subscription')
		subscription.party_type = 'Customer'
		subscription.party = '_Test Customer'
		subscription.append('plans', {'plan': '_Test Plan Name', 'qty': 1})
		subscription.start_date = '2018-01-01'
		subscription.insert()
		subscription.process()		# generate first invoice

		# Status is unpaid as Days until Due is zero and grace period is Zero
		self.assertEqual(subscription.status, 'Unpaid')

		subscription.cancel_subscription()
		self.assertEqual(subscription.status, 'Cancelled')

		subscription.restart_subscription()
		self.assertEqual(subscription.status, 'Active')
		self.assertEqual(len(subscription.invoices), 0)

		subscription.process()
		self.assertEqual(subscription.status, 'Active')
		self.assertEqual(len(subscription.invoices), 0)

		subscription.process()
		self.assertEqual(subscription.status, 'Active')
		self.assertEqual(len(subscription.invoices), 0)

		settings.cancel_after_grace = default_grace_period_action
		settings.save()
		subscription.delete()

	def test_subscription_unpaid_back_to_active(self):
		settings = frappe.get_single('Subscription Settings')
		default_grace_period_action = settings.cancel_after_grace
		settings.cancel_after_grace = 0
		settings.save()

		subscription = frappe.new_doc('Subscription')
		subscription.party_type = 'Customer'
		subscription.party = '_Test Customer'
		subscription.append('plans', {'plan': '_Test Plan Name', 'qty': 1})
		subscription.start_date = '2018-01-01'
		subscription.insert()

		subscription.process()		# generate first invoice
		# This should change status to Unpaid since grace period is 0
		self.assertEqual(subscription.status, 'Unpaid')

		invoice = subscription.get_current_invoice()
		invoice.db_set('outstanding_amount', 0)
		invoice.db_set('status', 'Paid')

		subscription.process()
		self.assertEqual(subscription.status, 'Active')

		# A new invoice is generated
		subscription.process()
		self.assertEqual(subscription.status, 'Unpaid')

		settings.cancel_after_grace = default_grace_period_action
		settings.save()
		subscription.delete()

	def test_restart_active_subscription(self):
		subscription = frappe.new_doc('Subscription')
		subscription.party_type = 'Customer'
		subscription.party = '_Test Customer'
		subscription.append('plans', {'plan': '_Test Plan Name', 'qty': 1})
		subscription.save()

		self.assertRaises(frappe.ValidationError, subscription.restart_subscription)

		subscription.delete()

	def test_subscription_invoice_discount_percentage(self):
		subscription = frappe.new_doc('Subscription')
		subscription.party_type = 'Customer'
		subscription.party = '_Test Customer'
		subscription.additional_discount_percentage = 10
		subscription.append('plans', {'plan': '_Test Plan Name', 'qty': 1})
		subscription.save()
		subscription.cancel_subscription()

		invoice = subscription.get_current_invoice()

		self.assertEqual(invoice.additional_discount_percentage, 10)
		self.assertEqual(invoice.apply_discount_on, 'Grand Total')

		subscription.delete()

	def test_subscription_invoice_discount_amount(self):
		subscription = frappe.new_doc('Subscription')
		subscription.party_type = 'Customer'
		subscription.party = '_Test Customer'
		subscription.additional_discount_amount = 11
		subscription.append('plans', {'plan': '_Test Plan Name', 'qty': 1})
		subscription.save()
		subscription.cancel_subscription()

		invoice = subscription.get_current_invoice()

		self.assertEqual(invoice.discount_amount, 11)
		self.assertEqual(invoice.apply_discount_on, 'Grand Total')

		subscription.delete()

	def test_prepaid_subscriptions(self):
		# Create a non pre-billed subscription, processing should not create
		# invoices.
		subscription = frappe.new_doc('Subscription')
		subscription.party_type = 'Customer'
		subscription.party = '_Test Customer'
		subscription.append('plans', {'plan': '_Test Plan Name', 'qty': 1})
		subscription.save()
		subscription.process()

		self.assertEqual(len(subscription.invoices), 0)

		# Change the subscription type to prebilled and process it.
		# Prepaid invoice should be generated
		subscription.generate_invoice_at_period_start = True
		subscription.save()
		subscription.process()

		self.assertEqual(len(subscription.invoices), 1)

	def test_prepaid_subscriptions_with_prorate_true(self):
		settings = frappe.get_single('Subscription Settings')
		to_prorate = settings.prorate
		settings.prorate = 1
		settings.save()

		subscription = frappe.new_doc('Subscription')
		subscription.party_type = 'Customer'
		subscription.party = '_Test Customer'
		subscription.generate_invoice_at_period_start = True
		subscription.append('plans', {'plan': '_Test Plan Name', 'qty': 1})
		subscription.save()
		subscription.process()
		subscription.cancel_subscription()

		self.assertEqual(len(subscription.invoices), 1)

		current_inv = subscription.get_current_invoice()
		self.assertEqual(current_inv.status, "Unpaid")

		prorate_factor = 1

		self.assertEqual(flt(current_inv.grand_total, 2), flt(prorate_factor * 900, 2))

		settings.prorate = to_prorate
		settings.save()

		subscription.delete()

	def test_subscription_with_follow_calendar_months(self):
		subscription = frappe.new_doc('Subscription')
		subscription.party_type = 'Supplier'
		subscription.party = '_Test Supplier'
		subscription.generate_invoice_at_period_start = 1
		subscription.follow_calendar_months = 1

		# select subscription start date as '2018-01-15'
		subscription.start_date = '2018-01-15'
		subscription.end_date = '2018-07-15'
		subscription.append('plans', {'plan': '_Test Plan Name 4', 'qty': 1})
		subscription.save()

		# even though subscription starts at '2018-01-15' and Billing interval is Month and count 3
		# First invoice will end at '2018-03-31' instead of '2018-04-14'
		self.assertEqual(get_date_str(subscription.current_invoice_end), '2018-03-31')

	def test_subscription_generate_invoice_past_due(self):
		subscription = frappe.new_doc('Subscription')
		subscription.party_type = 'Supplier'
		subscription.party = '_Test Supplier'
		subscription.generate_invoice_at_period_start = 1
		subscription.generate_new_invoices_past_due_date = 1
		# select subscription start date as '2018-01-15'
		subscription.start_date = '2018-01-01'
		subscription.append('plans', {'plan': '_Test Plan Name 4', 'qty': 1})
		subscription.save()

		# Process subscription and create first invoice
		# Subscription status will be unpaid since due date has already passed
		subscription.process()
		self.assertEqual(len(subscription.invoices), 1)
		self.assertEqual(subscription.status, 'Unpaid')

		# Now the Subscription is unpaid
		# Even then new invoice should be created as we have enabled `generate_new_invoices_past_due_date` in
		# subscription

		subscription.process()
		self.assertEqual(len(subscription.invoices), 2)

	def test_subscription_without_generate_invoice_past_due(self):
		subscription = frappe.new_doc('Subscription')
		subscription.party_type = 'Supplier'
		subscription.party = '_Test Supplier'
		subscription.generate_invoice_at_period_start = 1
		# select subscription start date as '2018-01-15'
		subscription.start_date = '2018-01-01'
		subscription.append('plans', {'plan': '_Test Plan Name 4', 'qty': 1})
		subscription.save()

		# Process subscription and create first invoice
		# Subscription status will be unpaid since due date has already passed
		subscription.process()
		self.assertEqual(len(subscription.invoices), 1)
		self.assertEqual(subscription.status, 'Unpaid')

		subscription.process()
		self.assertEqual(len(subscription.invoices), 1)


