# Copyright (c) 2017, Velometro Mobility Inc and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.utils import cint
import frappe

def execute(filters=None):
	wo_list = get_work_orders()
	data = get_item_list(wo_list, filters)
	columns = get_columns()
	return columns, data
	
def get_item_list(wo_list, filters):
	out = []
	
	#Add a row for each item/qty
	for wo_details in wo_list:
		desc = frappe.db.get_value("BOM", wo_details.bom_no, "description")

		for wo_item_details in frappe.db.get_values("Work Order Item",
			{"parent": wo_details.name}, ["item_code", "source_warehouse"], as_dict=1):

			item_list = frappe.db.sql("""SELECT
					bom_item.item_code as item_code,
					ifnull(ledger.actual_qty*bom.quantity/bom_item.stock_qty,0) as build_qty
				FROM
					`tabBOM` as bom, `tabBOM Item` AS bom_item
					LEFT JOIN `tabBin` AS ledger
						ON bom_item.item_code = ledger.item_code
						AND ledger.warehouse = ifnull(%(warehouse)s,%(filterhouse)s)
				WHERE
					bom.name = bom_item.parent
					and bom_item.item_code = %(item_code)s
					and bom.name = %(bom)s
				GROUP BY
					bom_item.item_code""",
			{"bom": wo_details.bom_no, "warehouse": wo_item_details.source_warehouse,
				"filterhouse": filters.warehouse, "item_code": wo_item_details.item_code}, as_dict=1)

			stock_qty = 0
			count = 0
			buildable_qty = wo_details.qty
			for item in item_list:
				count = count + 1
				if item.build_qty >= (wo_details.qty - wo_details.produced_qty):
					stock_qty = stock_qty + 1
				elif buildable_qty >= item.build_qty:
					buildable_qty = item.build_qty

			if count == stock_qty:
				build = "Y"
			else:
				build = "N"

			row = frappe._dict({
				"work_order": wo_details.name,
				"status": wo_details.status,
				"req_items": cint(count),
				"instock": stock_qty,
				"description": desc,
				"source_warehouse": wo_item_details.source_warehouse,
				"item_code": wo_item_details.item_code,
				"bom_no": wo_details.bom_no,
				"qty": wo_details.qty,
				"buildable_qty": buildable_qty,
				"ready_to_build": build
			})

			out.append(row)

	return out
	
def get_work_orders():
	out =  frappe.get_all("Work Order", filters={"docstatus": 1, "status": ( "!=","Completed")},
		fields=["name","status", "bom_no", "qty", "produced_qty"], order_by='name')

	return out
	
def get_columns():
	columns = [{
		"fieldname": "work_order",
		"label": "Work Order",
		"fieldtype": "Link",
		"options": "Work Order",
		"width": 110
	}, {
		"fieldname": "bom_no",
		"label": "BOM",
		"fieldtype": "Link",
		"options": "BOM",
		"width": 120
	}, {
		"fieldname": "description",
		"label": "Description",
		"fieldtype": "Data",
		"options": "",
		"width": 230
	}, {
		"fieldname": "item_code",
		"label": "Item Code",
		"fieldtype": "Link",
		"options": "Item",
		"width": 110
	},{
		"fieldname": "source_warehouse",
		"label": "Source Warehouse",
		"fieldtype": "Link",
		"options": "Warehouse",
		"width": 110
	},{
		"fieldname": "qty",
		"label": "Qty to Build",
		"fieldtype": "Data",
		"options": "",
		"width": 110
	}, {
		"fieldname": "status",
		"label": "Status",
		"fieldtype": "Data",
		"options": "",
		"width": 100
	}, {
		"fieldname": "req_items",
		"label": "# Req'd Items",
		"fieldtype": "Data",
		"options": "",
		"width": 105
	}, {
		"fieldname": "instock",
		"label": "# In Stock",
		"fieldtype": "Data",
		"options": "",
		"width": 105
	}, {
		"fieldname": "buildable_qty",
		"label": "Buildable Qty",
		"fieldtype": "Data",
		"options": "",
		"width": 100
	}, {
		"fieldname": "ready_to_build",
		"label": "Build All?",
		"fieldtype": "Data",
		"options": "",
		"width": 90
	}]

	return columns
