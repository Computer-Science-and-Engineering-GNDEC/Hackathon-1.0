# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'assessment_plan',
		'transactions': [
			{
				'label': _('Assessment'),
				'items': ['Assessment Result']
			}
		],
		'reports': [
			{
				'label': _('Report'),
				'items': ['Assessment Plan Status']
			}
		]
	}