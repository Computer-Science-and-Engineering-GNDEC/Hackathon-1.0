from __future__ import unicode_literals

import frappe
from frappe.model.db_query import DatabaseQuery

@frappe.whitelist()
def get_data(item_code=None, warehouse=None, item_group=None,
	start=0, sort_by='actual_qty', sort_order='desc'):
	'''Return data to render the item dashboard'''
	filters = []
	if item_code:
		filters.append(['item_code', '=', item_code])
	if warehouse:
		filters.append(['warehouse', '=', warehouse])
	if item_group:
		lft, rgt = frappe.db.get_value("Item Group", item_group, ["lft", "rgt"])
		items = frappe.db.sql_list("""
			select i.name from `tabItem` i
			where exists(select name from `tabItem Group`
				where name=i.item_group and lft >=%s and rgt<=%s)
		""", (lft, rgt))
		filters.append(['item_code', 'in', items])
	try:
		# check if user has any restrictions based on user permissions on warehouse
		if DatabaseQuery('Warehouse', user=frappe.session.user).build_match_conditions():
			filters.append(['warehouse', 'in', [w.name for w in frappe.get_list('Warehouse')]])
	except frappe.PermissionError:
		# user does not have access on warehouse
		return []

	items = frappe.db.get_all('Bin', fields=['item_code', 'warehouse', 'projected_qty',
			'reserved_qty', 'reserved_qty_for_production', 'reserved_qty_for_sub_contract', 'actual_qty', 'valuation_rate'],
		or_filters={
			'projected_qty': ['!=', 0],
			'reserved_qty': ['!=', 0],
			'reserved_qty_for_production': ['!=', 0],
			'reserved_qty_for_sub_contract': ['!=', 0],
			'actual_qty': ['!=', 0],
		},
		filters=filters,
		order_by=sort_by + ' ' + sort_order,
		limit_start=start,
		limit_page_length='21')

	for item in items:
		item.update({
			'item_name': frappe.get_cached_value("Item", item.item_code, 'item_name'),
			'disable_quick_entry': frappe.get_cached_value("Item", item.item_code, 'has_batch_no')
				or frappe.get_cached_value("Item", item.item_code, 'has_serial_no'),
		})

	return items
