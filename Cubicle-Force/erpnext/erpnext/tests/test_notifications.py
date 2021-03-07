# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
import unittest

from frappe.desk import notifications
from frappe.test_runner import make_test_objects

class TestNotifications(unittest.TestCase):
	def test_get_notifications_for_targets(self):
		'''
			Test notification config entries for targets as percentages
		'''

		company = frappe.get_all("Company")[0]
		frappe.db.set_value("Company", company.name, "monthly_sales_target", 10000)
		frappe.db.set_value("Company", company.name, "total_monthly_sales", 1000)

		config = notifications.get_notification_config()
		doc_target_percents = notifications.get_notifications_for_targets(config, {})

		self.assertEqual(doc_target_percents['Company'][company.name], 10)

		frappe.db.set_value("Company", company.name, "monthly_sales_target", 2000)
		frappe.db.set_value("Company", company.name, "total_monthly_sales", 0)

		config = notifications.get_notification_config()
		doc_target_percents = notifications.get_notifications_for_targets(config, {})

		self.assertEqual(doc_target_percents['Company'][company.name], 0)
