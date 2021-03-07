# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class ItemTaxTemplate(Document):
	def validate(self):
		self.validate_tax_accounts()

	def validate_tax_accounts(self):
		"""Check whether Tax Rate is not entered twice for same Tax Type"""
		check_list = []
		for d in self.get('taxes'):
			if d.tax_type:
				account_type = frappe.db.get_value("Account", d.tax_type, "account_type")

				if account_type not in ['Tax', 'Chargeable', 'Income Account', 'Expense Account', 'Expenses Included In Valuation']:
					frappe.throw(
						_("Item Tax Row {0} must have account of type Tax or Income or Expense or Chargeable").format(
							d.idx))
				else:
					if d.tax_type in check_list:
						frappe.throw(_("{0} entered twice in Item Tax").format(d.tax_type))
					else:
						check_list.append(d.tax_type)
