# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe.utils import cint, cstr, flt, today
from frappe import _
from erpnext.setup.utils import get_exchange_rate
from frappe.website.website_generator import WebsiteGenerator
from erpnext.stock.get_item_details import get_conversion_factor
from erpnext.stock.get_item_details import get_price_list_rate
from frappe.core.doctype.version.version import get_diff
from erpnext.controllers.queries import get_match_cond
from erpnext.stock.doctype.item.item import get_item_details
from frappe.model.mapper import get_mapped_doc

import functools

from six import string_types

from operator import itemgetter

form_grid_templates = {
	"items": "templates/form_grid/item_grid.html"
}

class BOM(WebsiteGenerator):
	website = frappe._dict(
		# page_title_field = "item_name",
		condition_field = "show_in_website",
		template = "templates/generators/bom.html"
	)

	def autoname(self):
		names = frappe.db.sql_list("""select name from `tabBOM` where item=%s""", self.item)

		if names:
			# name can be BOM/ITEM/001, BOM/ITEM/001-1, BOM-ITEM-001, BOM-ITEM-001-1

			# split by item
			names = [name.split(self.item, 1) for name in names]
			names = [d[-1][1:] for d in filter(lambda x: len(x) > 1 and x[-1], names)]

			# split by (-) if cancelled
			if names:
				names = [cint(name.split('-')[-1]) for name in names]
				idx = max(names) + 1
			else:
				idx = 1
		else:
			idx = 1

		name = 'BOM-' + self.item + ('-%.3i' % idx)
		if frappe.db.exists("BOM", name):
			conflicting_bom = frappe.get_doc("BOM", name)

			if conflicting_bom.item != self.item:
				msg = (_("A BOM with name {0} already exists for item {1}.")
					.format(frappe.bold(name), frappe.bold(conflicting_bom.item)))

				frappe.throw(_("{0}{1} Did you rename the item? Please contact Administrator / Tech support")
					.format(msg, "<br>"))

		self.name = name

	def validate(self):
		self.route = frappe.scrub(self.name).replace('_', '-')

		if not self.company:
			frappe.throw(_("Please select a Company first."), title=_("Mandatory"))

		self.clear_operations()
		self.validate_main_item()
		self.validate_currency()
		self.set_conversion_rate()
		self.set_plc_conversion_rate()
		self.validate_uom_is_interger()
		self.set_bom_material_details()
		self.validate_materials()
		self.set_routing_operations()
		self.validate_operations()
		self.calculate_cost()
		self.update_stock_qty()
		self.update_cost(update_parent=False, from_child_bom=True, save=False)

	def get_context(self, context):
		context.parents = [{'name': 'boms', 'title': _('All BOMs') }]

	def on_update(self):
		frappe.cache().hdel('bom_children', self.name)
		self.check_recursion()

	def on_submit(self):
		self.manage_default_bom()

	def on_cancel(self):
		frappe.db.set(self, "is_active", 0)
		frappe.db.set(self, "is_default", 0)

		# check if used in any other bom
		self.validate_bom_links()
		self.manage_default_bom()

	def on_update_after_submit(self):
		self.validate_bom_links()
		self.manage_default_bom()

	def get_item_det(self, item_code):
		item = get_item_details(item_code)

		if not item:
			frappe.throw(_("Item: {0} does not exist in the system").format(item_code))

		return item

	def get_routing(self):
		if self.routing:
			self.set("operations", [])
			fields = ["sequence_id", "operation", "workstation", "description",
				"time_in_mins", "batch_size", "operating_cost", "idx", "hour_rate"]

			for row in frappe.get_all("BOM Operation", fields = fields,
				filters = {'parenttype': 'Routing', 'parent': self.routing}, order_by="sequence_id, idx"):
				child = self.append('operations', row)
				child.hour_rate = flt(row.hour_rate / self.conversion_rate, 2)

	def set_bom_material_details(self):
		for item in self.get("items"):
			self.validate_bom_currecny(item)

			ret = self.get_bom_material_detail({
				"company": self.company,
				"item_code": item.item_code,
				"item_name": item.item_name,
				"bom_no": item.bom_no,
				"stock_qty": item.stock_qty,
				"include_item_in_manufacturing": item.include_item_in_manufacturing,
				"qty": item.qty,
				"uom": item.uom,
				"stock_uom": item.stock_uom,
				"conversion_factor": item.conversion_factor,
				"sourced_by_supplier": item.sourced_by_supplier
			})
			for r in ret:
				if not item.get(r):
					item.set(r, ret[r])

	def get_bom_material_detail(self, args=None):
		""" Get raw material details like uom, desc and rate"""
		if not args:
			args = frappe.form_dict.get('args')

		if isinstance(args, string_types):
			import json
			args = json.loads(args)

		item = self.get_item_det(args['item_code'])

		args['bom_no'] = args['bom_no'] or item and cstr(item['default_bom']) or ''
		args['transfer_for_manufacture'] = (cstr(args.get('include_item_in_manufacturing', '')) or
			item and item.include_item_in_manufacturing or 0)
		args.update(item)

		rate = self.get_rm_rate(args)
		ret_item = {
			 'item_name'	: item and args['item_name'] or '',
			 'description'  : item and args['description'] or '',
			 'image'		: item and args['image'] or '',
			 'stock_uom'	: item and args['stock_uom'] or '',
			 'uom'			: item and args['stock_uom'] or '',
 			 'conversion_factor': 1,
			 'bom_no'		: args['bom_no'],
			 'rate'			: rate,
			 'qty'			: args.get("qty") or args.get("stock_qty") or 1,
			 'stock_qty'	: args.get("qty") or args.get("stock_qty") or 1,
			 'base_rate'	: flt(rate) * (flt(self.conversion_rate) or 1),
			 'include_item_in_manufacturing': cint(args.get('transfer_for_manufacture')),
			 'sourced_by_supplier'		: args.get('sourced_by_supplier', 0)
		}

		return ret_item

	def validate_bom_currecny(self, item):
		if item.get('bom_no') and frappe.db.get_value('BOM', item.get('bom_no'), 'currency') != self.currency:
			frappe.throw(_("Row {0}: Currency of the BOM #{1} should be equal to the selected currency {2}")
				.format(item.idx, item.bom_no, self.currency))

	def get_rm_rate(self, arg):
		"""	Get raw material rate as per selected method, if bom exists takes bom cost """
		rate = 0
		if not self.rm_cost_as_per:
			self.rm_cost_as_per = "Valuation Rate"

		if arg.get('scrap_items'):
			rate = get_valuation_rate(arg)
		elif arg:
			#Customer Provided parts and Supplier sourced parts will have zero rate
			if not frappe.db.get_value('Item', arg["item_code"], 'is_customer_provided_item') and not arg.get('sourced_by_supplier'):
				if arg.get('bom_no') and self.set_rate_of_sub_assembly_item_based_on_bom:
					rate = flt(self.get_bom_unitcost(arg['bom_no'])) * (arg.get("conversion_factor") or 1)
				else:
					rate = get_bom_item_rate(arg, self)

					if not rate:
						if self.rm_cost_as_per == "Price List":
							frappe.msgprint(_("Price not found for item {0} in price list {1}")
								.format(arg["item_code"], self.buying_price_list), alert=True)
						else:
							frappe.msgprint(_("{0} not found for item {1}")
								.format(self.rm_cost_as_per, arg["item_code"]), alert=True)
		return flt(rate) * flt(self.plc_conversion_rate or 1) / (self.conversion_rate or 1)

	def update_cost(self, update_parent=True, from_child_bom=False, save=True):
		if self.docstatus == 2:
			return

		existing_bom_cost = self.total_cost

		for d in self.get("items"):
			rate = self.get_rm_rate({
				"company": self.company,
				"item_code": d.item_code,
				"bom_no": d.bom_no,
				"qty": d.qty,
				"uom": d.uom,
				"stock_uom": d.stock_uom,
				"conversion_factor": d.conversion_factor,
				"sourced_by_supplier": d.sourced_by_supplier
			})

			if rate:
				d.rate = rate
			d.amount = flt(d.rate) * flt(d.qty)
			d.base_rate = flt(d.rate) * flt(self.conversion_rate)
			d.base_amount = flt(d.amount) * flt(self.conversion_rate)

			if save:
				d.db_update()

		if self.docstatus == 1:
			self.flags.ignore_validate_update_after_submit = True
			self.calculate_cost()
		if save:
			self.db_update()

		self.update_exploded_items(save=save)

		# update parent BOMs
		if self.total_cost != existing_bom_cost and update_parent:
			parent_boms = frappe.db.sql_list("""select distinct parent from `tabBOM Item`
				where bom_no = %s and docstatus=1 and parenttype='BOM'""", self.name)

			for bom in parent_boms:
				frappe.get_doc("BOM", bom).update_cost(from_child_bom=True)

		if not from_child_bom:
			frappe.msgprint(_("Cost Updated"))

	def update_parent_cost(self):
		if self.total_cost:
			cost = self.total_cost / self.quantity

			frappe.db.sql("""update `tabBOM Item` set rate=%s, amount=stock_qty*%s
				where bom_no = %s and docstatus < 2 and parenttype='BOM'""",
				(cost, cost, self.name))

	def get_bom_unitcost(self, bom_no):
		bom = frappe.db.sql("""select name, base_total_cost/quantity as unit_cost from `tabBOM`
			where is_active = 1 and name = %s""", bom_no, as_dict=1)
		return bom and bom[0]['unit_cost'] or 0

	def manage_default_bom(self):
		""" Uncheck others if current one is selected as default or
			check the current one as default if it the only bom for the selected item,
			update default bom in item master
		"""
		if self.is_default and self.is_active:
			from frappe.model.utils import set_default
			set_default(self, "item")
			item = frappe.get_doc("Item", self.item)
			if item.default_bom != self.name:
				frappe.db.set_value('Item', self.item, 'default_bom', self.name)
		elif not frappe.db.exists(dict(doctype='BOM', docstatus=1, item=self.item, is_default=1)) \
			and self.is_active:
			frappe.db.set(self, "is_default", 1)
		else:
			frappe.db.set(self, "is_default", 0)
			item = frappe.get_doc("Item", self.item)
			if item.default_bom == self.name:
				frappe.db.set_value('Item', self.item, 'default_bom', None)

	def clear_operations(self):
		if not self.with_operations:
			self.set('operations', [])

	def validate_main_item(self):
		""" Validate main FG item"""
		item = self.get_item_det(self.item)
		if not item:
			frappe.throw(_("Item {0} does not exist in the system or has expired").format(self.item))
		else:
			ret = frappe.db.get_value("Item", self.item, ["description", "stock_uom", "item_name"])
			self.description = ret[0]
			self.uom = ret[1]
			self.item_name= ret[2]

		if not self.quantity:
			frappe.throw(_("Quantity should be greater than 0"))

	def validate_currency(self):
		if self.rm_cost_as_per == 'Price List':
			price_list_currency = frappe.db.get_value('Price List', self.buying_price_list, 'currency')
			if price_list_currency not in (self.currency, self.company_currency()):
				frappe.throw(_("Currency of the price list {0} must be {1} or {2}")
					.format(self.buying_price_list, self.currency, self.company_currency()))

	def update_stock_qty(self):
		for m in self.get('items'):
			if not m.conversion_factor:
				m.conversion_factor = flt(get_conversion_factor(m.item_code, m.uom)['conversion_factor'])
			if m.uom and m.qty:
				m.stock_qty = flt(m.conversion_factor)*flt(m.qty)
			if not m.uom and m.stock_uom:
				m.uom = m.stock_uom
				m.qty = m.stock_qty

	def validate_uom_is_interger(self):
		from erpnext.utilities.transaction_base import validate_uom_is_integer
		validate_uom_is_integer(self, "uom", "qty", "BOM Item")
		validate_uom_is_integer(self, "stock_uom", "stock_qty", "BOM Item")

	def set_conversion_rate(self):
		if self.currency == self.company_currency():
			self.conversion_rate = 1
		elif self.conversion_rate == 1 or flt(self.conversion_rate) <= 0:
			self.conversion_rate = get_exchange_rate(self.currency, self.company_currency(), args="for_buying")

	def set_plc_conversion_rate(self):
		if self.rm_cost_as_per in ["Valuation Rate", "Last Purchase Rate"]:
			self.plc_conversion_rate = 1
		elif not self.plc_conversion_rate and self.price_list_currency:
			self.plc_conversion_rate = get_exchange_rate(self.price_list_currency,
				self.company_currency(), args="for_buying")

	def validate_materials(self):
		""" Validate raw material entries """

		if not self.get('items'):
			frappe.throw(_("Raw Materials cannot be blank."))

		check_list = []
		for m in self.get('items'):
			if m.bom_no:
				validate_bom_no(m.item_code, m.bom_no)
			if flt(m.qty) <= 0:
				frappe.throw(_("Quantity required for Item {0} in row {1}").format(m.item_code, m.idx))
			check_list.append(m)

	def check_recursion(self, bom_list=[]):
		""" Check whether recursion occurs in any bom"""
		bom_list = self.traverse_tree()
		bom_nos = frappe.get_all('BOM Item', fields=["bom_no"],
			filters={'parent': ('in', bom_list), 'parenttype': 'BOM'})

		raise_exception = False
		if bom_nos and self.name in [d.bom_no for d in bom_nos]:
			raise_exception = True

		if not raise_exception:
			bom_nos = frappe.get_all('BOM Item', fields=["parent"],
				filters={'bom_no': self.name, 'parenttype': 'BOM'})

			if self.name in [d.parent for d in bom_nos]:
				raise_exception = True

		if raise_exception:
			frappe.throw(_("BOM recursion: {0} cannot be parent or child of {1}").format(self.name, self.name))

	def traverse_tree(self, bom_list=None):
		def _get_children(bom_no):
			children = frappe.cache().hget('bom_children', bom_no)
			if children is None:
				children = frappe.db.sql_list("""SELECT `bom_no` FROM `tabBOM Item`
					WHERE `parent`=%s AND `bom_no`!='' AND `parenttype`='BOM'""", bom_no)
				frappe.cache().hset('bom_children', bom_no, children)
			return children

		count = 0
		if not bom_list:
			bom_list = []

		if self.name not in bom_list:
			bom_list.append(self.name)

		while(count < len(bom_list)):
			for child_bom in _get_children(bom_list[count]):
				if child_bom not in bom_list:
					bom_list.append(child_bom)
			count += 1
		bom_list.reverse()
		return bom_list

	def calculate_cost(self):
		"""Calculate bom totals"""
		self.calculate_op_cost()
		self.calculate_rm_cost()
		self.calculate_sm_cost()
		self.total_cost = self.operating_cost + self.raw_material_cost - self.scrap_material_cost
		self.base_total_cost = self.base_operating_cost + self.base_raw_material_cost - self.base_scrap_material_cost

	def calculate_op_cost(self):
		"""Update workstation rate and calculates totals"""
		self.operating_cost = 0
		self.base_operating_cost = 0
		for d in self.get('operations'):
			if d.workstation:
				if not d.hour_rate:
					hour_rate = flt(frappe.db.get_value("Workstation", d.workstation, "hour_rate"))
					d.hour_rate = hour_rate / flt(self.conversion_rate) if self.conversion_rate else hour_rate

			if d.hour_rate and d.time_in_mins:
				d.base_hour_rate = flt(d.hour_rate) * flt(self.conversion_rate)
				d.operating_cost = flt(d.hour_rate) * flt(d.time_in_mins) / 60.0
				d.base_operating_cost = flt(d.operating_cost) * flt(self.conversion_rate)

			self.operating_cost += flt(d.operating_cost)
			self.base_operating_cost += flt(d.base_operating_cost)

	def calculate_rm_cost(self):
		"""Fetch RM rate as per today's valuation rate and calculate totals"""
		total_rm_cost = 0
		base_total_rm_cost = 0

		for d in self.get('items'):
			d.base_rate = flt(d.rate) * flt(self.conversion_rate)
			d.amount = flt(d.rate, d.precision("rate")) * flt(d.qty, d.precision("qty"))
			d.base_amount = d.amount * flt(self.conversion_rate)
			d.qty_consumed_per_unit = flt(d.stock_qty, d.precision("stock_qty")) \
				/ flt(self.quantity, self.precision("quantity"))

			total_rm_cost += d.amount
			base_total_rm_cost += d.base_amount

		self.raw_material_cost = total_rm_cost
		self.base_raw_material_cost = base_total_rm_cost

	def calculate_sm_cost(self):
		"""Fetch RM rate as per today's valuation rate and calculate totals"""
		total_sm_cost = 0
		base_total_sm_cost = 0

		for d in self.get('scrap_items'):
			d.base_rate = flt(d.rate, d.precision("rate")) * flt(self.conversion_rate, self.precision("conversion_rate"))
			d.amount = flt(d.rate, d.precision("rate")) * flt(d.stock_qty, d.precision("stock_qty"))
			d.base_amount = flt(d.amount, d.precision("amount")) * flt(self.conversion_rate, self.precision("conversion_rate"))
			total_sm_cost += d.amount
			base_total_sm_cost += d.base_amount

		self.scrap_material_cost = total_sm_cost
		self.base_scrap_material_cost = base_total_sm_cost

	def update_new_bom(self, old_bom, new_bom, rate):
		for d in self.get("items"):
			if d.bom_no != old_bom: continue

			d.bom_no = new_bom
			d.rate = rate
			d.amount = (d.stock_qty or d.qty) * rate

	def update_exploded_items(self, save=True):
		""" Update Flat BOM, following will be correct data"""
		self.get_exploded_items()
		self.add_exploded_items(save=save)

	def get_exploded_items(self):
		""" Get all raw materials including items from child bom"""
		self.cur_exploded_items = {}
		for d in self.get('items'):
			if d.bom_no:
				self.get_child_exploded_items(d.bom_no, d.stock_qty)
			else:
				self.add_to_cur_exploded_items(frappe._dict({
					'item_code'		: d.item_code,
					'item_name'		: d.item_name,
					'operation'		: d.operation,
					'source_warehouse': d.source_warehouse,
					'description'	: d.description,
					'image'			: d.image,
					'stock_uom'		: d.stock_uom,
					'stock_qty'		: flt(d.stock_qty),
					'rate'			: flt(d.base_rate) / (flt(d.conversion_factor) or 1.0),
					'include_item_in_manufacturing': d.include_item_in_manufacturing,
					'sourced_by_supplier': d.sourced_by_supplier
				}))

	def company_currency(self):
		return erpnext.get_company_currency(self.company)

	def add_to_cur_exploded_items(self, args):
		if self.cur_exploded_items.get(args.item_code):
			self.cur_exploded_items[args.item_code]["stock_qty"] += args.stock_qty
		else:
			self.cur_exploded_items[args.item_code] = args

	def get_child_exploded_items(self, bom_no, stock_qty):
		""" Add all items from Flat BOM of child BOM"""
		# Did not use qty_consumed_per_unit in the query, as it leads to rounding loss
		child_fb_items = frappe.db.sql("""
			SELECT
				bom_item.item_code,
				bom_item.item_name,
				bom_item.description,
				bom_item.source_warehouse,
				bom_item.operation,
				bom_item.stock_uom,
				bom_item.stock_qty,
				bom_item.rate,
				bom_item.include_item_in_manufacturing,
				bom_item.sourced_by_supplier,
				bom_item.stock_qty / ifnull(bom.quantity, 1) AS qty_consumed_per_unit
			FROM `tabBOM Explosion Item` bom_item, tabBOM bom
			WHERE
				bom_item.parent = bom.name
				AND bom.name = %s
				AND bom.docstatus = 1
		""", bom_no, as_dict = 1)

		for d in child_fb_items:
			self.add_to_cur_exploded_items(frappe._dict({
				'item_code'				: d['item_code'],
				'item_name'				: d['item_name'],
				'source_warehouse'		: d['source_warehouse'],
				'operation'				: d['operation'],
				'description'			: d['description'],
				'stock_uom'				: d['stock_uom'],
				'stock_qty'				: d['qty_consumed_per_unit'] * stock_qty,
				'rate'					: flt(d['rate']),
				'include_item_in_manufacturing': d.get('include_item_in_manufacturing', 0),
				'sourced_by_supplier': d.get('sourced_by_supplier', 0)
			}))

	def add_exploded_items(self, save=True):
		"Add items to Flat BOM table"
		self.set('exploded_items', [])

		if save:
			frappe.db.sql("""delete from `tabBOM Explosion Item` where parent=%s""", self.name)

		for d in sorted(self.cur_exploded_items, key=itemgetter(0)):
			ch = self.append('exploded_items', {})
			for i in self.cur_exploded_items[d].keys():
				ch.set(i, self.cur_exploded_items[d][i])
			ch.amount = flt(ch.stock_qty) * flt(ch.rate)
			ch.qty_consumed_per_unit = flt(ch.stock_qty) / flt(self.quantity)
			ch.docstatus = self.docstatus

			if save:
				ch.db_insert()

	def validate_bom_links(self):
		if not self.is_active:
			act_pbom = frappe.db.sql("""select distinct bom_item.parent from `tabBOM Item` bom_item
				where bom_item.bom_no = %s and bom_item.docstatus = 1 and bom_item.parenttype='BOM'
				and exists (select * from `tabBOM` where name = bom_item.parent
					and docstatus = 1 and is_active = 1)""", self.name)

			if act_pbom and act_pbom[0][0]:
				frappe.throw(_("Cannot deactivate or cancel BOM as it is linked with other BOMs"))

	def set_routing_operations(self):
		if self.routing and self.with_operations and not self.operations:
			self.get_routing()

	def validate_operations(self):
		if self.with_operations and not self.get('operations'):
			frappe.throw(_("Operations cannot be left blank"))

		if self.with_operations:
			for d in self.operations:
				if not d.description:
					d.description = frappe.db.get_value('Operation', d.operation, 'description')
				if not d.batch_size or d.batch_size <= 0:
					d.batch_size = 1

def get_bom_item_rate(args, bom_doc):
	if bom_doc.rm_cost_as_per == 'Valuation Rate':
		rate = get_valuation_rate(args) * (args.get("conversion_factor") or 1)
	elif bom_doc.rm_cost_as_per == 'Last Purchase Rate':
		rate = ( flt(args.get('last_purchase_rate')) \
			or frappe.db.get_value("Item", args['item_code'], "last_purchase_rate")) \
				* (args.get("conversion_factor") or 1)
	elif bom_doc.rm_cost_as_per == "Price List":
		if not bom_doc.buying_price_list:
			frappe.throw(_("Please select Price List"))
		bom_args = frappe._dict({
			"doctype": "BOM",
			"price_list": bom_doc.buying_price_list,
			"qty": args.get("qty") or 1,
			"uom": args.get("uom") or args.get("stock_uom"),
			"stock_uom": args.get("stock_uom"),
			"transaction_type": "buying",
			"company": bom_doc.company,
			"currency": bom_doc.currency,
			"conversion_rate": 1, # Passed conversion rate as 1 purposefully, as conversion rate is applied at the end of the function
			"conversion_factor": args.get("conversion_factor") or 1,
			"plc_conversion_rate": 1,
			"ignore_party": True
		})
		item_doc = frappe.get_cached_doc("Item", args.get("item_code"))
		out = frappe._dict()
		get_price_list_rate(bom_args, item_doc, out)
		rate = out.price_list_rate

	return rate

def get_valuation_rate(args):
	""" Get weighted average of valuation rate from all warehouses """

	total_qty, total_value, valuation_rate = 0.0, 0.0, 0.0
	item_bins = frappe.db.sql("""
		select
			bin.actual_qty, bin.stock_value
		from
			`tabBin` bin, `tabWarehouse` warehouse
		where
			bin.item_code=%(item)s
			and bin.warehouse = warehouse.name
			and warehouse.company=%(company)s""",
		{"item": args['item_code'], "company": args['company']}, as_dict=1)

	for d in item_bins:
		total_qty += flt(d.actual_qty)
		total_value += flt(d.stock_value)

	if total_qty:
		valuation_rate =  total_value / total_qty

	if valuation_rate <= 0:
		last_valuation_rate = frappe.db.sql("""select valuation_rate
			from `tabStock Ledger Entry`
			where item_code = %s and valuation_rate > 0
			order by posting_date desc, posting_time desc, creation desc limit 1""", args['item_code'])

		valuation_rate = flt(last_valuation_rate[0][0]) if last_valuation_rate else 0

	if not valuation_rate:
		valuation_rate = frappe.db.get_value("Item", args['item_code'], "valuation_rate")

	return flt(valuation_rate)

def get_list_context(context):
	context.title = _("Bill of Materials")
	# context.introduction = _('Boms')

def get_bom_items_as_dict(bom, company, qty=1, fetch_exploded=1, fetch_scrap_items=0, include_non_stock_items=False, fetch_qty_in_stock_uom=True):
	item_dict = {}

	# Did not use qty_consumed_per_unit in the query, as it leads to rounding loss
	query = """select
				bom_item.item_code,
				bom_item.idx,
				item.item_name,
				sum(bom_item.{qty_field}/ifnull(bom.quantity, 1)) * %(qty)s as qty,
				item.image,
				bom.project,
				bom_item.rate,
				bom_item.amount,
				item.stock_uom,
				item.item_group,
				item.allow_alternative_item,
				item_default.default_warehouse,
				item_default.expense_account as expense_account,
				item_default.buying_cost_center as cost_center
				{select_columns}
			from
				`tab{table}` bom_item
				JOIN `tabBOM` bom ON bom_item.parent = bom.name
				JOIN `tabItem` item ON item.name = bom_item.item_code
				LEFT JOIN `tabItem Default` item_default
					ON item_default.parent = item.name and item_default.company = %(company)s
			where
				bom_item.docstatus < 2
				and bom.name = %(bom)s
				and ifnull(item.has_variants, 0) = 0
				and item.is_stock_item in (1, {is_stock_item})
				{where_conditions}
				group by item_code, stock_uom
				order by idx"""

	is_stock_item = 0 if include_non_stock_items else 1
	if cint(fetch_exploded):
		query = query.format(table="BOM Explosion Item",
			where_conditions="",
			is_stock_item=is_stock_item,
			qty_field="stock_qty",
			select_columns = """, bom_item.source_warehouse, bom_item.operation,
				bom_item.include_item_in_manufacturing, bom_item.description, bom_item.rate, bom_item.sourced_by_supplier,
				(Select idx from `tabBOM Item` where item_code = bom_item.item_code and parent = %(parent)s limit 1) as idx""")

		items = frappe.db.sql(query, { "parent": bom, "qty": qty, "bom": bom, "company": company }, as_dict=True)
	elif fetch_scrap_items:
		query = query.format(table="BOM Scrap Item", where_conditions="",
			select_columns=", bom_item.idx, item.description", is_stock_item=is_stock_item, qty_field="stock_qty")

		items = frappe.db.sql(query, { "qty": qty, "bom": bom, "company": company }, as_dict=True)
	else:
		query = query.format(table="BOM Item", where_conditions="", is_stock_item=is_stock_item,
			qty_field="stock_qty" if fetch_qty_in_stock_uom else "qty",
			select_columns = """, bom_item.uom, bom_item.conversion_factor, bom_item.source_warehouse,
				bom_item.idx, bom_item.operation, bom_item.include_item_in_manufacturing, bom_item.sourced_by_supplier,
				bom_item.description, bom_item.base_rate as rate """)
		items = frappe.db.sql(query, { "qty": qty, "bom": bom, "company": company }, as_dict=True)

	for item in items:
		if item.item_code in item_dict:
			item_dict[item.item_code]["qty"] += flt(item.qty)
		else:
			item_dict[item.item_code] = item

	for item, item_details in item_dict.items():
		for d in [["Account", "expense_account", "stock_adjustment_account"],
			["Cost Center", "cost_center", "cost_center"], ["Warehouse", "default_warehouse", ""]]:
				company_in_record = frappe.db.get_value(d[0], item_details.get(d[1]), "company")
				if not item_details.get(d[1]) or (company_in_record and company != company_in_record):
					item_dict[item][d[1]] = frappe.get_cached_value('Company',  company,  d[2]) if d[2] else None

	return item_dict

@frappe.whitelist()
def get_bom_items(bom, company, qty=1, fetch_exploded=1):
	items = get_bom_items_as_dict(bom, company, qty, fetch_exploded, include_non_stock_items=True).values()
	items = list(items)
	items.sort(key = functools.cmp_to_key(lambda a, b: a.item_code > b.item_code and 1 or -1))
	return items

def validate_bom_no(item, bom_no):
	"""Validate BOM No of sub-contracted items"""
	bom = frappe.get_doc("BOM", bom_no)
	if not bom.is_active:
		frappe.throw(_("BOM {0} must be active").format(bom_no))
	if bom.docstatus != 1:
		if not getattr(frappe.flags, "in_test", False):
			frappe.throw(_("BOM {0} must be submitted").format(bom_no))
	if item:
		rm_item_exists = False
		for d in bom.items:
			if (d.item_code.lower() == item.lower()):
				rm_item_exists = True
		for d in bom.scrap_items:
			if (d.item_code.lower() == item.lower()):
				rm_item_exists = True
		if bom.item.lower() == item.lower() or \
			bom.item.lower() == cstr(frappe.db.get_value("Item", item, "variant_of")).lower():
 				rm_item_exists = True
		if not rm_item_exists:
			frappe.throw(_("BOM {0} does not belong to Item {1}").format(bom_no, item))

@frappe.whitelist()
def get_children(doctype, parent=None, is_root=False, **filters):
	if not parent or parent=="BOM":
		frappe.msgprint(_('Please select a BOM'))
		return

	if parent:
		frappe.form_dict.parent = parent

	if frappe.form_dict.parent:
		bom_doc = frappe.get_doc("BOM", frappe.form_dict.parent)
		frappe.has_permission("BOM", doc=bom_doc, throw=True)

		bom_items = frappe.get_all('BOM Item',
			fields=['item_code', 'bom_no as value', 'stock_qty'],
			filters=[['parent', '=', frappe.form_dict.parent]],
			order_by='idx')

		item_names = tuple(d.get('item_code') for d in bom_items)

		items = frappe.get_list('Item',
			fields=['image', 'description', 'name', 'stock_uom', 'item_name'],
			filters=[['name', 'in', item_names]]) # to get only required item dicts

		for bom_item in bom_items:
			# extend bom_item dict with respective item dict
			bom_item.update(
				# returns an item dict from items list which matches with item_code
				next(item for item in items if item.get('name')
					== bom_item.get('item_code'))
			)

			bom_item.parent_bom_qty = bom_doc.quantity
			bom_item.expandable = 0 if bom_item.value in ('', None)  else 1

		return bom_items

def get_boms_in_bottom_up_order(bom_no=None):
	def _get_parent(bom_no):
		return frappe.db.sql_list("""
			select distinct bom_item.parent from `tabBOM Item` bom_item
			where bom_item.bom_no = %s and bom_item.docstatus=1 and bom_item.parenttype='BOM'
				and exists(select bom.name from `tabBOM` bom where bom.name=bom_item.parent and bom.is_active=1)
		""", bom_no)

	count = 0
	bom_list = []
	if bom_no:
		bom_list.append(bom_no)
	else:
		# get all leaf BOMs
		bom_list = frappe.db.sql_list("""select name from `tabBOM` bom
			where docstatus=1 and is_active=1
				and not exists(select bom_no from `tabBOM Item`
					where parent=bom.name and ifnull(bom_no, '')!='')""")

	while(count < len(bom_list)):
		for child_bom in _get_parent(bom_list[count]):
			if child_bom not in bom_list:
				bom_list.append(child_bom)
		count += 1

	return bom_list

def add_additional_cost(stock_entry, work_order):
	# Add non stock items cost in the additional cost
	stock_entry.additional_costs = []
	expenses_included_in_valuation = frappe.get_cached_value("Company", work_order.company,
		"expenses_included_in_valuation")

	add_non_stock_items_cost(stock_entry, work_order, expenses_included_in_valuation)
	add_operations_cost(stock_entry, work_order, expenses_included_in_valuation)

def add_non_stock_items_cost(stock_entry, work_order, expense_account):
	bom = frappe.get_doc('BOM', work_order.bom_no)
	table = 'exploded_items' if work_order.get('use_multi_level_bom') else 'items'

	items = {}
	for d in bom.get(table):
		items.setdefault(d.item_code, d.amount)

	non_stock_items = frappe.get_all('Item',
		fields="name", filters={'name': ('in', list(items.keys())), 'ifnull(is_stock_item, 0)': 0}, as_list=1)

	non_stock_items_cost = 0.0
	for name in non_stock_items:
		non_stock_items_cost += flt(items.get(name[0])) * flt(stock_entry.fg_completed_qty) / flt(bom.quantity)

	if non_stock_items_cost:
		stock_entry.append('additional_costs', {
			'expense_account': expense_account,
			'description': _("Non stock items"),
			'amount': non_stock_items_cost
		})

def add_operations_cost(stock_entry, work_order=None, expense_account=None):
	from erpnext.stock.doctype.stock_entry.stock_entry import get_operating_cost_per_unit
	operating_cost_per_unit = get_operating_cost_per_unit(work_order, stock_entry.bom_no)

	if operating_cost_per_unit:
		stock_entry.append('additional_costs', {
			"expense_account": expense_account,
			"description": _("Operating Cost as per Work Order / BOM"),
			"amount": operating_cost_per_unit * flt(stock_entry.fg_completed_qty)
		})

	if work_order and work_order.additional_operating_cost and work_order.qty:
		additional_operating_cost_per_unit = \
			flt(work_order.additional_operating_cost) / flt(work_order.qty)

		if additional_operating_cost_per_unit:
			stock_entry.append('additional_costs', {
				"expense_account": expense_account,
				"description": "Additional Operating Cost",
				"amount": additional_operating_cost_per_unit * flt(stock_entry.fg_completed_qty)
			})

@frappe.whitelist()
def get_bom_diff(bom1, bom2):
	from frappe.model import table_fields

	if bom1 == bom2:
		frappe.throw(_("BOM 1 {0} and BOM 2 {1} should not be same")
			.format(frappe.bold(bom1), frappe.bold(bom2)))

	doc1 = frappe.get_doc('BOM', bom1)
	doc2 = frappe.get_doc('BOM', bom2)

	out = get_diff(doc1, doc2)
	out.row_changed = []
	out.added = []
	out.removed = []

	meta = doc1.meta

	identifiers = {
		'operations': 'operation',
		'items': 'item_code',
		'scrap_items': 'item_code',
		'exploded_items': 'item_code'
	}

	for df in meta.fields:
		old_value, new_value = doc1.get(df.fieldname), doc2.get(df.fieldname)

		if df.fieldtype in table_fields:
			identifier = identifiers[df.fieldname]
			# make maps
			old_row_by_identifier, new_row_by_identifier = {}, {}
			for d in old_value:
				old_row_by_identifier[d.get(identifier)] = d
			for d in new_value:
				new_row_by_identifier[d.get(identifier)] = d

			# check rows for additions, changes
			for i, d in enumerate(new_value):
				if d.get(identifier) in old_row_by_identifier:
					diff = get_diff(old_row_by_identifier[d.get(identifier)], d, for_child=True)
					if diff and diff.changed:
						out.row_changed.append((df.fieldname, i, d.get(identifier), diff.changed))
				else:
					out.added.append([df.fieldname, d.as_dict()])

			# check for deletions
			for d in old_value:
				if not d.get(identifier) in new_row_by_identifier:
					out.removed.append([df.fieldname, d.as_dict()])

	return out

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def item_query(doctype, txt, searchfield, start, page_len, filters):
	meta = frappe.get_meta("Item", cached=True)
	searchfields = meta.get_search_fields()

	order_by = "idx desc, name, item_name"

	fields = ["name", "item_group", "item_name", "description"]
	fields.extend([field for field in searchfields
		if not field in ["name", "item_group", "description"]])

	searchfields = searchfields + [field for field in [searchfield or "name", "item_code", "item_group", "item_name"]
		if not field in searchfields]

	query_filters = {
		"disabled": 0,
		"ifnull(end_of_life, '5050-50-50')": (">", today())
	}

	or_cond_filters = {}
	if txt:
		for s_field in searchfields:
			or_cond_filters[s_field] = ("like", "%{0}%".format(txt))

		barcodes = frappe.get_all("Item Barcode",
			fields=["distinct parent as item_code"],
			filters = {"barcode": ("like", "%{0}%".format(txt))})

		barcodes = [d.item_code for d in barcodes]
		if barcodes:
			or_cond_filters["name"] = ("in", barcodes)

	for cond in get_match_cond(doctype, as_condition=False):
		for key, value in cond.items():
			if key == doctype:
				key = "name"

			query_filters[key] = ("in", value)

	if filters and filters.get("item_code"):
		has_variants = frappe.get_cached_value("Item", filters.get("item_code"), "has_variants")
		if not has_variants:
			query_filters["has_variants"] = 0

	return frappe.get_all("Item",
		fields = fields, filters=query_filters,
		or_filters = or_cond_filters, order_by=order_by,
		limit_start=start, limit_page_length=page_len, as_list=1)

@frappe.whitelist()
def make_variant_bom(source_name, bom_no, item, variant_items, target_doc=None):
	from erpnext.manufacturing.doctype.work_order.work_order import add_variant_item

	def postprocess(source, doc):
		doc.item = item
		doc.quantity = 1

		item_data = get_item_details(item)
		doc.update({
			"item_name": item_data.item_name,
			"description": item_data.description,
			"uom": item_data.stock_uom,
			"allow_alternative_item": item_data.allow_alternative_item
		})

		add_variant_item(variant_items, doc, source_name)

	doc = get_mapped_doc('BOM', source_name, {
		'BOM': {
			'doctype': 'BOM',
			'validation': {
				'docstatus': ['=', 1]
			}
		},
		'BOM Item': {
			'doctype': 'BOM Item',
			'condition': lambda doc: doc.has_variants == 0
		},
	}, target_doc, postprocess)

	return doc
