from __future__ import unicode_literals

data = {
	'desktop_icons': [
		'Restaurant',
		'Hotels',
		'Accounts',
		'Buying',
		'Stock',
		'HR',
		'Project',
		'ToDo'
	],
	'restricted_roles': [
		'Restaurant Manager',
		'Hotel Manager',
		'Hotel Reservation User'
	],
	'custom_fields': {
		'Sales Invoice': [
			{
				'fieldname': 'restaurant', 'fieldtype': 'Link', 'options': 'Restaurant',
				'insert_after': 'customer_name', 'label': 'Restaurant',
			},
			{
				'fieldname': 'restaurant_table', 'fieldtype': 'Link', 'options': 'Restaurant Table',
				'insert_after': 'restaurant', 'label': 'Restaurant Table',
			}
		],
		'Price List': [
			{
				'fieldname':'restaurant_menu', 'fieldtype':'Link', 'options':'Restaurant Menu', 'label':'Restaurant Menu',
				'insert_after':'currency'
			}
		]
	}
}
