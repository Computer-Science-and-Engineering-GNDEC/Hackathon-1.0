# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt
from __future__ import unicode_literals
import frappe

import unittest, os, json
from frappe.utils import cstr
from erpnext.erpnext_integrations.connectors.shopify_connection import create_order
from erpnext.erpnext_integrations.doctype.shopify_settings.sync_product import make_item
from erpnext.erpnext_integrations.doctype.shopify_settings.sync_customer import create_customer
from frappe.core.doctype.data_import.data_import import import_doc


class ShopifySettings(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")

		# use the fixture data
		import_doc(path=frappe.get_app_path("erpnext", "erpnext_integrations/doctype/shopify_settings/test_data/custom_field.json"),
			ignore_links=True, overwrite=True)

		frappe.reload_doctype("Customer")
		frappe.reload_doctype("Sales Order")
		frappe.reload_doctype("Delivery Note")
		frappe.reload_doctype("Sales Invoice")

		self.setup_shopify()

	def setup_shopify(self):
		shopify_settings = frappe.get_doc("Shopify Settings")
		shopify_settings.taxes = []

		shopify_settings.update({
			"app_type": "Private",
			"shopify_url": "test.myshopify.com",
			"api_key": "17702c7c4452b9c5d235240b6e7a39da",
			"password": "17702c7c4452b9c5d235240b6e7a39da",
			"shared_secret": "17702c7c4452b9c5d235240b6e7a39da",
			"price_list": "_Test Price List",
			"warehouse": "_Test Warehouse - _TC",
			"cash_bank_account": "Cash - _TC",
			"account": "Cash - _TC",
			"customer_group": "_Test Customer Group",
			"cost_center": "Main - _TC",
			"taxes": [
				{
					"shopify_tax": "International Shipping",
					"tax_account":"Legal Expenses - _TC"
				}
			],
			"enable_shopify": 0,
			"sales_order_series": "SO-",
			"sync_sales_invoice": 1,
			"sales_invoice_series": "SINV-",
			"sync_delivery_note": 1,
			"delivery_note_series": "DN-"
		}).save(ignore_permissions=True)

		self.shopify_settings = shopify_settings

	def test_order(self):
		### Create Customer ###
		with open (os.path.join(os.path.dirname(__file__), "test_data", "shopify_customer.json")) as shopify_customer:
			shopify_customer = json.load(shopify_customer)
		create_customer(shopify_customer.get("customer"), self.shopify_settings)

		### Create Item ###
		with open (os.path.join(os.path.dirname(__file__), "test_data", "shopify_item.json")) as shopify_item:
			shopify_item = json.load(shopify_item)
		make_item("_Test Warehouse - _TC", shopify_item.get("product"))


		### Create Order ###
		with open (os.path.join(os.path.dirname(__file__), "test_data", "shopify_order.json")) as shopify_order:
			shopify_order = json.load(shopify_order)

		create_order(shopify_order.get("order"), self.shopify_settings, False, company="_Test Company")

		sales_order = frappe.get_doc("Sales Order", {"shopify_order_id": cstr(shopify_order.get("order").get("id"))})

		self.assertEqual(cstr(shopify_order.get("order").get("id")), sales_order.shopify_order_id)

		#check for customer
		shopify_order_customer_id = cstr(shopify_order.get("order").get("customer").get("id"))
		sales_order_customer_id = frappe.get_value("Customer", sales_order.customer, "shopify_customer_id")

		self.assertEqual(shopify_order_customer_id, sales_order_customer_id)

		#check sales invoice
		sales_invoice = frappe.get_doc("Sales Invoice", {"shopify_order_id": sales_order.shopify_order_id})
		self.assertEqual(sales_invoice.rounded_total, sales_order.rounded_total)

		#check delivery note
		delivery_note_count = frappe.db.sql("""select count(*) from `tabDelivery Note`
			where shopify_order_id = %s""", sales_order.shopify_order_id)[0][0]

		self.assertEqual(delivery_note_count, len(shopify_order.get("order").get("fulfillments")))
