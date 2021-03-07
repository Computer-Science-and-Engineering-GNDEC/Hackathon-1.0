from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'delivery_note',
		'non_standard_fieldnames': {
			'Stock Entry': 'delivery_note_no',
			'Quality Inspection': 'reference_name',
			'Auto Repeat': 'reference_document',
		},
		'internal_links': {
			'Sales Order': ['items', 'against_sales_order'],
		},
		'transactions': [
			{
				'label': _('Related'),
				'items': ['Sales Invoice', 'Packing Slip', 'Delivery Trip']
			},
			{
				'label': _('Reference'),
				'items': ['Sales Order', 'Shipment', 'Quality Inspection']
			},
			{
				'label': _('Returns'),
				'items': ['Stock Entry']
			},
			{
				'label': _('Subscription'),
				'items': ['Auto Repeat']
			},
		]
	}