from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'pick_list',
		'transactions': [
			{
				'items': ['Stock Entry', 'Delivery Note']
			},
		]
	}