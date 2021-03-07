# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
from __future__ import unicode_literals

import frappe, erpnext
from frappe import _
from frappe.utils import cint, flt, cstr, now, now_datetime
from frappe.model.meta import get_field_precision
from erpnext.stock.utils import get_valuation_method, get_incoming_outgoing_rate_for_cancel
from erpnext.stock.utils import get_bin
import json
from six import iteritems

# future reposting
class NegativeStockError(frappe.ValidationError): pass

_exceptions = frappe.local('stockledger_exceptions')
# _exceptions = []

def make_sl_entries(sl_entries, allow_negative_stock=False, via_landed_cost_voucher=False):
	if sl_entries:
		from erpnext.stock.utils import update_bin

		cancel = sl_entries[0].get("is_cancelled")
		if cancel:
			validate_cancellation(sl_entries)
			set_as_cancel(sl_entries[0].get('voucher_type'), sl_entries[0].get('voucher_no'))

		for sle in sl_entries:
			if cancel:
				sle['actual_qty'] = -flt(sle.get('actual_qty'))

				if sle['actual_qty'] < 0 and not sle.get('outgoing_rate'):
					sle['outgoing_rate'] = get_incoming_outgoing_rate_for_cancel(sle.item_code,
						sle.voucher_type, sle.voucher_no, sle.voucher_detail_no)
					sle['incoming_rate'] = 0.0

				if sle['actual_qty'] > 0 and not sle.get('incoming_rate'):
					sle['incoming_rate'] = get_incoming_outgoing_rate_for_cancel(sle.item_code,
						sle.voucher_type, sle.voucher_no, sle.voucher_detail_no)
					sle['outgoing_rate'] = 0.0

			if sle.get("actual_qty") or sle.get("voucher_type")=="Stock Reconciliation":
				sle_doc = make_entry(sle, allow_negative_stock, via_landed_cost_voucher)

			args = sle_doc.as_dict()
			update_bin(args, allow_negative_stock, via_landed_cost_voucher)

def validate_cancellation(args):
	if args[0].get("is_cancelled"):
		repost_entry = frappe.db.get_value("Repost Item Valuation", {
			'voucher_type': args[0].voucher_type,
			'voucher_no': args[0].voucher_no,
			'docstatus': 1
		}, ['name', 'status'], as_dict=1)

		if repost_entry:
			if repost_entry.status == 'In Progress':
				frappe.throw(_("Cannot cancel the transaction. Reposting of item valuation on submission is not completed yet."))
			if repost_entry.status == 'Queued':
				doc = frappe.get_doc("Repost Item Valuation", repost_entry.name)
				doc.cancel()
				doc.delete()

def set_as_cancel(voucher_type, voucher_no):
	frappe.db.sql("""update `tabStock Ledger Entry` set is_cancelled=1,
		modified=%s, modified_by=%s
		where voucher_type=%s and voucher_no=%s and is_cancelled = 0""",
		(now(), frappe.session.user, voucher_type, voucher_no))

def make_entry(args, allow_negative_stock=False, via_landed_cost_voucher=False):
	args.update({"doctype": "Stock Ledger Entry"})
	sle = frappe.get_doc(args)
	sle.flags.ignore_permissions = 1
	sle.allow_negative_stock=allow_negative_stock
	sle.via_landed_cost_voucher = via_landed_cost_voucher
	sle.insert()
	sle.submit()
	return sle

def repost_future_sle(args=None, voucher_type=None, voucher_no=None, allow_negative_stock=None, via_landed_cost_voucher=False):
	if not args and voucher_type and voucher_no:
		args = get_args_for_voucher(voucher_type, voucher_no)

	distinct_item_warehouses = [(d.item_code, d.warehouse) for d in args]

	i = 0
	while i < len(args):
		obj = update_entries_after({
			"item_code": args[i].item_code,
			"warehouse": args[i].warehouse,
			"posting_date": args[i].posting_date,
			"posting_time": args[i].posting_time,
			"creation": args[i].get("creation")
		}, allow_negative_stock=allow_negative_stock, via_landed_cost_voucher=via_landed_cost_voucher)

		for item_wh, new_sle in iteritems(obj.new_items):
			if item_wh not in distinct_item_warehouses:
				args.append(new_sle)

		i += 1

def get_args_for_voucher(voucher_type, voucher_no):
	return frappe.db.get_all("Stock Ledger Entry",
		filters={"voucher_type": voucher_type, "voucher_no": voucher_no},
		fields=["item_code", "warehouse", "posting_date", "posting_time", "creation"],
		order_by="creation asc",
		group_by="item_code, warehouse"
	)

class update_entries_after(object):
	"""
		update valution rate and qty after transaction
		from the current time-bucket onwards

		:param args: args as dict

			args = {
				"item_code": "ABC",
				"warehouse": "XYZ",
				"posting_date": "2012-12-12",
				"posting_time": "12:00"
			}
	"""
	def __init__(self, args, allow_zero_rate=False, allow_negative_stock=None, via_landed_cost_voucher=False, verbose=1):
		self.exceptions = {}
		self.verbose = verbose
		self.allow_zero_rate = allow_zero_rate
		self.via_landed_cost_voucher = via_landed_cost_voucher
		self.allow_negative_stock = allow_negative_stock \
			or cint(frappe.db.get_single_value("Stock Settings", "allow_negative_stock"))

		self.args = frappe._dict(args)
		self.item_code = args.get("item_code")
		if self.args.sle_id:
			self.args['name'] = self.args.sle_id

		self.company = frappe.get_cached_value("Warehouse", self.args.warehouse, "company")
		self.get_precision()
		self.valuation_method = get_valuation_method(self.item_code)
		self.new_items = {}

		self.data = frappe._dict()
		self.initialize_previous_data(self.args)

		self.build()

	def get_precision(self):
		company_base_currency = frappe.get_cached_value('Company',  self.company,  "default_currency")
		self.precision = get_field_precision(frappe.get_meta("Stock Ledger Entry").get_field("stock_value"),
			currency=company_base_currency)

	def initialize_previous_data(self, args):
		"""
			Get previous sl entries for current item for each related warehouse
			and assigns into self.data dict

			:Data Structure:

			self.data = {
				warehouse1: {
					'previus_sle': {},
					'qty_after_transaction': 10,
					'valuation_rate': 100,
					'stock_value': 1000,
					'prev_stock_value': 1000,
					'stock_queue': '[[10, 100]]',
					'stock_value_difference': 1000
				}
			}

		"""
		self.data.setdefault(args.warehouse, frappe._dict())
		warehouse_dict = self.data[args.warehouse]
		previous_sle = self.get_previous_sle_of_current_voucher(args)
		warehouse_dict.previous_sle = previous_sle

		for key in ("qty_after_transaction", "valuation_rate", "stock_value"):
			setattr(warehouse_dict, key, flt(previous_sle.get(key)))

		warehouse_dict.update({
			"prev_stock_value": previous_sle.stock_value or 0.0,
			"stock_queue": json.loads(previous_sle.stock_queue or "[]"),
			"stock_value_difference": 0.0
		})

	def get_previous_sle_of_current_voucher(self, args):
		"""get stock ledger entries filtered by specific posting datetime conditions"""

		args['time_format'] = '%H:%i:%s'
		if not args.get("posting_date"):
			args["posting_date"] = "1900-01-01"
		if not args.get("posting_time"):
			args["posting_time"] = "00:00"

		sle = frappe.db.sql("""
			select *, timestamp(posting_date, posting_time) as "timestamp"
			from `tabStock Ledger Entry`
			where item_code = %(item_code)s
				and warehouse = %(warehouse)s
				and is_cancelled = 0
				and timestamp(posting_date, time_format(posting_time, %(time_format)s)) < timestamp(%(posting_date)s, time_format(%(posting_time)s, %(time_format)s))
			order by timestamp(posting_date, posting_time) desc, creation desc
			limit 1""", args, as_dict=1)

		return sle[0] if sle else frappe._dict()


	def build(self):
		from erpnext.controllers.stock_controller import check_if_future_sle_exists

		if self.args.get("sle_id"):
			self.process_sle_against_current_timestamp()
			if not check_if_future_sle_exists(self.args):
				self.update_bin()
		else:
			entries_to_fix = self.get_future_entries_to_fix()

			i = 0
			while i < len(entries_to_fix):
				sle = entries_to_fix[i]
				i += 1

				self.process_sle(sle)

				if sle.dependant_sle_voucher_detail_no:
					entries_to_fix = self.get_dependent_entries_to_fix(entries_to_fix, sle)

			self.update_bin()

		if self.exceptions:
			self.raise_exceptions()

	def process_sle_against_current_timestamp(self):
		sl_entries = self.get_sle_against_current_voucher()
		for sle in sl_entries:
			self.process_sle(sle)

	def get_sle_against_current_voucher(self):
		self.args['time_format'] = '%H:%i:%s'

		return frappe.db.sql("""
			select
				*, timestamp(posting_date, posting_time) as "timestamp"
			from
				`tabStock Ledger Entry`
			where
				item_code = %(item_code)s
				and warehouse = %(warehouse)s
				and timestamp(posting_date, time_format(posting_time, %(time_format)s)) = timestamp(%(posting_date)s, time_format(%(posting_time)s, %(time_format)s))

			order by
				creation ASC
			for update
		""", self.args, as_dict=1)

	def get_future_entries_to_fix(self):
		# includes current entry!
		args = self.data[self.args.warehouse].previous_sle \
			or frappe._dict({"item_code": self.item_code, "warehouse": self.args.warehouse})

		return list(self.get_sle_after_datetime(args))

	def get_dependent_entries_to_fix(self, entries_to_fix, sle):
		dependant_sle = get_sle_by_voucher_detail_no(sle.dependant_sle_voucher_detail_no,
			excluded_sle=sle.name)

		if not dependant_sle:
			return entries_to_fix
		elif dependant_sle.item_code == self.item_code and dependant_sle.warehouse == self.args.warehouse:
			return entries_to_fix
		elif dependant_sle.item_code != self.item_code:
			if (dependant_sle.item_code, dependant_sle.warehouse) not in self.new_items:
				self.new_items[(dependant_sle.item_code, dependant_sle.warehouse)] = dependant_sle
			return entries_to_fix
		elif dependant_sle.item_code == self.item_code and dependant_sle.warehouse in self.data:
			return entries_to_fix
		self.initialize_previous_data(dependant_sle)

		args = self.data[dependant_sle.warehouse].previous_sle \
			or frappe._dict({"item_code": self.item_code, "warehouse": dependant_sle.warehouse})
		future_sle_for_dependant = list(self.get_sle_after_datetime(args))

		entries_to_fix.extend(future_sle_for_dependant)
		return sorted(entries_to_fix, key=lambda k: k['timestamp'])

	def process_sle(self, sle):
		# previous sle data for this warehouse
		self.wh_data = self.data[sle.warehouse]

		if (sle.serial_no and not self.via_landed_cost_voucher) or not cint(self.allow_negative_stock):
			# validate negative stock for serialized items, fifo valuation
			# or when negative stock is not allowed for moving average
			if not self.validate_negative_stock(sle):
				self.wh_data.qty_after_transaction += flt(sle.actual_qty)
				return

		# Get dynamic incoming/outgoing rate
		self.get_dynamic_incoming_outgoing_rate(sle)

		if sle.serial_no:
			self.get_serialized_values(sle)
			self.wh_data.qty_after_transaction += flt(sle.actual_qty)
			if sle.voucher_type == "Stock Reconciliation":
				self.wh_data.qty_after_transaction = sle.qty_after_transaction

			self.wh_data.stock_value = flt(self.wh_data.qty_after_transaction) * flt(self.wh_data.valuation_rate)
		else:
			if sle.voucher_type=="Stock Reconciliation" and not sle.batch_no:
				# assert
				self.wh_data.valuation_rate = sle.valuation_rate
				self.wh_data.qty_after_transaction = sle.qty_after_transaction
				self.wh_data.stock_queue = [[self.wh_data.qty_after_transaction, self.wh_data.valuation_rate]]
				self.wh_data.stock_value = flt(self.wh_data.qty_after_transaction) * flt(self.wh_data.valuation_rate)
			else:
				if self.valuation_method == "Moving Average":
					self.get_moving_average_values(sle)
					self.wh_data.qty_after_transaction += flt(sle.actual_qty)
					self.wh_data.stock_value = flt(self.wh_data.qty_after_transaction) * flt(self.wh_data.valuation_rate)
				else:
					self.get_fifo_values(sle)
					self.wh_data.qty_after_transaction += flt(sle.actual_qty)
					self.wh_data.stock_value = sum((flt(batch[0]) * flt(batch[1]) for batch in self.wh_data.stock_queue))

		# rounding as per precision
		self.wh_data.stock_value = flt(self.wh_data.stock_value, self.precision)
		stock_value_difference = self.wh_data.stock_value - self.wh_data.prev_stock_value
		self.wh_data.prev_stock_value = self.wh_data.stock_value

		# update current sle
		sle.qty_after_transaction = self.wh_data.qty_after_transaction
		sle.valuation_rate = self.wh_data.valuation_rate
		sle.stock_value = self.wh_data.stock_value
		sle.stock_queue = json.dumps(self.wh_data.stock_queue)
		sle.stock_value_difference = stock_value_difference
		sle.doctype="Stock Ledger Entry"
		frappe.get_doc(sle).db_update()

		self.update_outgoing_rate_on_transaction(sle)

	def validate_negative_stock(self, sle):
		"""
			validate negative stock for entries current datetime onwards
			will not consider cancelled entries
		"""
		diff = self.wh_data.qty_after_transaction + flt(sle.actual_qty)

		if diff < 0 and abs(diff) > 0.0001:
			# negative stock!
			exc = sle.copy().update({"diff": diff})
			self.exceptions.setdefault(sle.warehouse, []).append(exc)
			return False
		else:
			return True

	def get_dynamic_incoming_outgoing_rate(self, sle):
		# Get updated incoming/outgoing rate from transaction
		if sle.recalculate_rate:
			rate = self.get_incoming_outgoing_rate_from_transaction(sle)

			if flt(sle.actual_qty) >= 0:
				sle.incoming_rate = rate
			else:
				sle.outgoing_rate = rate

	def get_incoming_outgoing_rate_from_transaction(self, sle):
		rate = 0
		# Material Transfer, Repack, Manufacturing
		if sle.voucher_type == "Stock Entry":
			rate = frappe.db.get_value("Stock Entry Detail", sle.voucher_detail_no, "valuation_rate")
		# Sales and Purchase Return
		elif sle.voucher_type in ("Purchase Receipt", "Purchase Invoice", "Delivery Note", "Sales Invoice"):
			if frappe.get_cached_value(sle.voucher_type, sle.voucher_no, "is_return"):
				from erpnext.controllers.sales_and_purchase_return import get_rate_for_return # don't move this import to top
				rate = get_rate_for_return(sle.voucher_type, sle.voucher_no, sle.item_code, voucher_detail_no=sle.voucher_detail_no)
			else:
				if sle.voucher_type in ("Purchase Receipt", "Purchase Invoice"):
					rate_field = "valuation_rate"
				else:
					rate_field = "incoming_rate"

				# check in item table
				item_code, incoming_rate = frappe.db.get_value(sle.voucher_type + " Item",
					sle.voucher_detail_no, ["item_code", rate_field])

				if item_code == sle.item_code:
					rate = incoming_rate
				else:
					if sle.voucher_type in ("Delivery Note", "Sales Invoice"):
						ref_doctype = "Packed Item"
					else:
						ref_doctype = "Purchase Receipt Item Supplied"

					rate = frappe.db.get_value(ref_doctype, {"parent_detail_docname": sle.voucher_detail_no,
						"item_code": sle.item_code}, rate_field)

		return rate

	def update_outgoing_rate_on_transaction(self, sle):
		"""
			Update outgoing rate in Stock Entry, Delivery Note, Sales Invoice and Sales Return
			In case of Stock Entry, also calculate FG Item rate and total incoming/outgoing amount
		"""
		if sle.actual_qty and sle.voucher_detail_no:
			outgoing_rate = abs(flt(sle.stock_value_difference)) / abs(sle.actual_qty)

			if flt(sle.actual_qty) < 0 and sle.voucher_type == "Stock Entry":
				self.update_rate_on_stock_entry(sle, outgoing_rate)
			elif sle.voucher_type in ("Delivery Note", "Sales Invoice"):
				self.update_rate_on_delivery_and_sales_return(sle, outgoing_rate)
			elif flt(sle.actual_qty) < 0 and sle.voucher_type in ("Purchase Receipt", "Purchase Invoice"):
				self.update_rate_on_purchase_receipt(sle, outgoing_rate)

	def update_rate_on_stock_entry(self, sle, outgoing_rate):
		frappe.db.set_value("Stock Entry Detail", sle.voucher_detail_no, "basic_rate", outgoing_rate)

		# Update outgoing item's rate, recalculate FG Item's rate and total incoming/outgoing amount
		stock_entry = frappe.get_doc("Stock Entry", sle.voucher_no)
		stock_entry.calculate_rate_and_amount(reset_outgoing_rate=False, raise_error_if_no_rate=False)
		stock_entry.db_update()
		for d in stock_entry.items:
			d.db_update()

	def update_rate_on_delivery_and_sales_return(self, sle, outgoing_rate):
		# Update item's incoming rate on transaction
		item_code = frappe.db.get_value(sle.voucher_type + " Item", sle.voucher_detail_no, "item_code")
		if item_code == sle.item_code:
			frappe.db.set_value(sle.voucher_type + " Item", sle.voucher_detail_no, "incoming_rate", outgoing_rate)
		else:
			# packed item
			frappe.db.set_value("Packed Item",
				{"parent_detail_docname": sle.voucher_detail_no, "item_code": sle.item_code},
				"incoming_rate", outgoing_rate)

	def update_rate_on_purchase_receipt(self, sle, outgoing_rate):
		if frappe.db.exists(sle.voucher_type + " Item", sle.voucher_detail_no):
			frappe.db.set_value(sle.voucher_type + " Item", sle.voucher_detail_no, "base_net_rate", outgoing_rate)
		else:
			frappe.db.set_value("Purchase Receipt Item Supplied", sle.voucher_detail_no, "rate", outgoing_rate)

		# Recalculate subcontracted item's rate in case of subcontracted purchase receipt/invoice
		if frappe.db.get_value(sle.voucher_type, sle.voucher_no, "is_subcontracted"):
			doc = frappe.get_doc(sle.voucher_type, sle.voucher_no)
			doc.update_valuation_rate(reset_outgoing_rate=False)
			for d in (doc.items + doc.supplied_items):
				d.db_update()

	def get_serialized_values(self, sle):
		incoming_rate = flt(sle.incoming_rate)
		actual_qty = flt(sle.actual_qty)
		serial_nos = cstr(sle.serial_no).split("\n")

		if incoming_rate < 0:
			# wrong incoming rate
			incoming_rate = self.wh_data.valuation_rate

		stock_value_change = 0
		if incoming_rate:
			stock_value_change = actual_qty * incoming_rate
		elif actual_qty < 0:
			# In case of delivery/stock issue, get average purchase rate
			# of serial nos of current entry
			if not sle.is_cancelled:
				outgoing_value = self.get_incoming_value_for_serial_nos(sle, serial_nos)
				stock_value_change = -1 * outgoing_value
			else:
				stock_value_change = actual_qty * sle.outgoing_rate

		new_stock_qty = self.wh_data.qty_after_transaction + actual_qty

		if new_stock_qty > 0:
			new_stock_value = (self.wh_data.qty_after_transaction * self.wh_data.valuation_rate) + stock_value_change
			if new_stock_value >= 0:
				# calculate new valuation rate only if stock value is positive
				# else it remains the same as that of previous entry
				self.wh_data.valuation_rate = new_stock_value / new_stock_qty

		if not self.wh_data.valuation_rate and sle.voucher_detail_no:
			allow_zero_rate = self.check_if_allow_zero_valuation_rate(sle.voucher_type, sle.voucher_detail_no)
			if not allow_zero_rate:
				self.wh_data.valuation_rate = get_valuation_rate(sle.item_code, sle.warehouse,
					sle.voucher_type, sle.voucher_no, self.allow_zero_rate,
					currency=erpnext.get_company_currency(sle.company))

	def get_incoming_value_for_serial_nos(self, sle, serial_nos):
		# get rate from serial nos within same company
		all_serial_nos = frappe.get_all("Serial No",
			fields=["purchase_rate", "name", "company"],
			filters = {'name': ('in', serial_nos)})

		incoming_values = sum([flt(d.purchase_rate) for d in all_serial_nos if d.company==sle.company])

		# Get rate for serial nos which has been transferred to other company
		invalid_serial_nos = [d.name for d in all_serial_nos if d.company!=sle.company]
		for serial_no in invalid_serial_nos:
			incoming_rate = frappe.db.sql("""
				select incoming_rate
				from `tabStock Ledger Entry`
				where
					company = %s
					and actual_qty > 0
					and (serial_no = %s
						or serial_no like %s
						or serial_no like %s
						or serial_no like %s
					)
				order by posting_date desc
				limit 1
			""", (sle.company, serial_no, serial_no+'\n%', '%\n'+serial_no, '%\n'+serial_no+'\n%'))

			incoming_values += flt(incoming_rate[0][0]) if incoming_rate else 0

		return incoming_values

	def get_moving_average_values(self, sle):
		actual_qty = flt(sle.actual_qty)
		new_stock_qty = flt(self.wh_data.qty_after_transaction) + actual_qty
		if new_stock_qty >= 0:
			if actual_qty > 0:
				if flt(self.wh_data.qty_after_transaction) <= 0:
					self.wh_data.valuation_rate = sle.incoming_rate
				else:
					new_stock_value = (self.wh_data.qty_after_transaction * self.wh_data.valuation_rate) + \
						(actual_qty * sle.incoming_rate)

					self.wh_data.valuation_rate = new_stock_value / new_stock_qty

			elif sle.outgoing_rate:
				if new_stock_qty:
					new_stock_value = (self.wh_data.qty_after_transaction * self.wh_data.valuation_rate) + \
						(actual_qty * sle.outgoing_rate)

					self.wh_data.valuation_rate = new_stock_value / new_stock_qty
				else:
					self.wh_data.valuation_rate = sle.outgoing_rate
		else:
			if flt(self.wh_data.qty_after_transaction) >= 0 and sle.outgoing_rate:
				self.wh_data.valuation_rate = sle.outgoing_rate

			if not self.wh_data.valuation_rate and actual_qty > 0:
				self.wh_data.valuation_rate = sle.incoming_rate

			# Get valuation rate from previous SLE or Item master, if item does not have the
			# allow zero valuration rate flag set
			if not self.wh_data.valuation_rate and sle.voucher_detail_no:
				allow_zero_valuation_rate = self.check_if_allow_zero_valuation_rate(sle.voucher_type, sle.voucher_detail_no)
				if not allow_zero_valuation_rate:
					self.wh_data.valuation_rate = get_valuation_rate(sle.item_code, sle.warehouse,
						sle.voucher_type, sle.voucher_no, self.allow_zero_rate,
						currency=erpnext.get_company_currency(sle.company))

	def get_fifo_values(self, sle):
		incoming_rate = flt(sle.incoming_rate)
		actual_qty = flt(sle.actual_qty)
		outgoing_rate = flt(sle.outgoing_rate)

		if actual_qty > 0:
			if not self.wh_data.stock_queue:
				self.wh_data.stock_queue.append([0, 0])

			# last row has the same rate, just updated the qty
			if self.wh_data.stock_queue[-1][1]==incoming_rate:
				self.wh_data.stock_queue[-1][0] += actual_qty
			else:
				if self.wh_data.stock_queue[-1][0] > 0:
					self.wh_data.stock_queue.append([actual_qty, incoming_rate])
				else:
					qty = self.wh_data.stock_queue[-1][0] + actual_qty
					self.wh_data.stock_queue[-1] = [qty, incoming_rate]
		else:
			qty_to_pop = abs(actual_qty)
			while qty_to_pop:
				if not self.wh_data.stock_queue:
					# Get valuation rate from last sle if exists or from valuation rate field in item master
					allow_zero_valuation_rate = self.check_if_allow_zero_valuation_rate(sle.voucher_type, sle.voucher_detail_no)
					if not allow_zero_valuation_rate:
						_rate = get_valuation_rate(sle.item_code, sle.warehouse,
							sle.voucher_type, sle.voucher_no, self.allow_zero_rate,
							currency=erpnext.get_company_currency(sle.company))
					else:
						_rate = 0

					self.wh_data.stock_queue.append([0, _rate])

				index = None
				if outgoing_rate > 0:
					# Find the entry where rate matched with outgoing rate
					for i, v in enumerate(self.wh_data.stock_queue):
						if v[1] == outgoing_rate:
							index = i
							break

					# If no entry found with outgoing rate, collapse stack
					if index == None:
						new_stock_value = sum((d[0]*d[1] for d in self.wh_data.stock_queue)) - qty_to_pop*outgoing_rate
						new_stock_qty = sum((d[0] for d in self.wh_data.stock_queue)) - qty_to_pop
						self.wh_data.stock_queue = [[new_stock_qty, new_stock_value/new_stock_qty if new_stock_qty > 0 else outgoing_rate]]
						break
				else:
					index = 0

				# select first batch or the batch with same rate
				batch = self.wh_data.stock_queue[index]
				if qty_to_pop >= batch[0]:
					# consume current batch
					qty_to_pop = qty_to_pop - batch[0]
					self.wh_data.stock_queue.pop(index)
					if not self.wh_data.stock_queue and qty_to_pop:
						# stock finished, qty still remains to be withdrawn
						# negative stock, keep in as a negative batch
						self.wh_data.stock_queue.append([-qty_to_pop, outgoing_rate or batch[1]])
						break

				else:
					# qty found in current batch
					# consume it and exit
					batch[0] = batch[0] - qty_to_pop
					qty_to_pop = 0

		stock_value = sum((flt(batch[0]) * flt(batch[1]) for batch in self.wh_data.stock_queue))
		stock_qty = sum((flt(batch[0]) for batch in self.wh_data.stock_queue))

		if stock_qty:
			self.wh_data.valuation_rate = stock_value / flt(stock_qty)

		if not self.wh_data.stock_queue:
			self.wh_data.stock_queue.append([0, sle.incoming_rate or sle.outgoing_rate or self.wh_data.valuation_rate])

	def check_if_allow_zero_valuation_rate(self, voucher_type, voucher_detail_no):
		ref_item_dt = ""

		if voucher_type == "Stock Entry":
			ref_item_dt = voucher_type + " Detail"
		elif voucher_type in ["Purchase Invoice", "Sales Invoice", "Delivery Note", "Purchase Receipt"]:
			ref_item_dt = voucher_type + " Item"

		if ref_item_dt:
			return frappe.db.get_value(ref_item_dt, voucher_detail_no, "allow_zero_valuation_rate")
		else:
			return 0

	def get_sle_before_datetime(self, args):
		"""get previous stock ledger entry before current time-bucket"""
		sle = get_stock_ledger_entries(args, "<", "desc", "limit 1", for_update=False)
		sle = sle[0] if sle else frappe._dict()
		return sle

	def get_sle_after_datetime(self, args):
		"""get Stock Ledger Entries after a particular datetime, for reposting"""
		return get_stock_ledger_entries(args, ">", "asc", for_update=True, check_serial_no=False)

	def raise_exceptions(self):
		msg_list = []
		for warehouse, exceptions in iteritems(self.exceptions):
			deficiency = min(e["diff"] for e in exceptions)

			if ((exceptions[0]["voucher_type"], exceptions[0]["voucher_no"]) in
				frappe.local.flags.currently_saving):

				msg = _("{0} units of {1} needed in {2} to complete this transaction.").format(
					abs(deficiency), frappe.get_desk_link('Item', exceptions[0]["item_code"]),
					frappe.get_desk_link('Warehouse', warehouse))
			else:
				msg = _("{0} units of {1} needed in {2} on {3} {4} for {5} to complete this transaction.").format(
					abs(deficiency), frappe.get_desk_link('Item', exceptions[0]["item_code"]),
					frappe.get_desk_link('Warehouse', warehouse),
					exceptions[0]["posting_date"], exceptions[0]["posting_time"],
					frappe.get_desk_link(exceptions[0]["voucher_type"], exceptions[0]["voucher_no"]))

			if msg:
				msg_list.append(msg)

		if msg_list:
			message = "\n\n".join(msg_list)
			if self.verbose:
				frappe.throw(message, NegativeStockError, title='Insufficient Stock')
			else:
				raise NegativeStockError(message)

	def update_bin(self):
		# update bin for each warehouse
		for warehouse, data in iteritems(self.data):
			bin_doc = get_bin(self.item_code, warehouse)
			bin_doc.update({
				"valuation_rate": data.valuation_rate,
				"actual_qty": data.qty_after_transaction,
				"stock_value": data.stock_value
			})
			bin_doc.flags.via_stock_ledger_entry = True
			bin_doc.save(ignore_permissions=True)

def get_previous_sle(args, for_update=False):
	"""
		get the last sle on or before the current time-bucket,
		to get actual qty before transaction, this function
		is called from various transaction like stock entry, reco etc

		args = {
			"item_code": "ABC",
			"warehouse": "XYZ",
			"posting_date": "2012-12-12",
			"posting_time": "12:00",
			"sle": "name of reference Stock Ledger Entry"
		}
	"""
	args["name"] = args.get("sle", None) or ""
	sle = get_stock_ledger_entries(args, "<=", "desc", "limit 1", for_update=for_update)
	return sle and sle[0] or {}

def get_stock_ledger_entries(previous_sle, operator=None,
	order="desc", limit=None, for_update=False, debug=False, check_serial_no=True):
	"""get stock ledger entries filtered by specific posting datetime conditions"""
	conditions = " and timestamp(posting_date, posting_time) {0} timestamp(%(posting_date)s, %(posting_time)s)".format(operator)
	if previous_sle.get("warehouse"):
		conditions += " and warehouse = %(warehouse)s"
	elif previous_sle.get("warehouse_condition"):
		conditions += " and " + previous_sle.get("warehouse_condition")

	if check_serial_no and previous_sle.get("serial_no"):
		conditions += " and serial_no like {}".format(frappe.db.escape('%{0}%'.format(previous_sle.get("serial_no"))))

	if not previous_sle.get("posting_date"):
		previous_sle["posting_date"] = "1900-01-01"
	if not previous_sle.get("posting_time"):
		previous_sle["posting_time"] = "00:00"

	if operator in (">", "<=") and previous_sle.get("name"):
		conditions += " and name!=%(name)s"

	return frappe.db.sql("""
		select *, timestamp(posting_date, posting_time) as "timestamp"
		from `tabStock Ledger Entry`
		where item_code = %%(item_code)s
		and is_cancelled = 0
		%(conditions)s
		order by timestamp(posting_date, posting_time) %(order)s, creation %(order)s
		%(limit)s %(for_update)s""" % {
			"conditions": conditions,
			"limit": limit or "",
			"for_update": for_update and "for update" or "",
			"order": order
		}, previous_sle, as_dict=1, debug=debug)

def get_sle_by_voucher_detail_no(voucher_detail_no, excluded_sle=None):
	return frappe.db.get_value('Stock Ledger Entry',
		{'voucher_detail_no': voucher_detail_no, 'name': ['!=', excluded_sle]},
		['item_code', 'warehouse', 'posting_date', 'posting_time', 'timestamp(posting_date, posting_time) as timestamp'],
		as_dict=1)

def get_valuation_rate(item_code, warehouse, voucher_type, voucher_no,
	allow_zero_rate=False, currency=None, company=None, raise_error_if_no_rate=True):
	# Get valuation rate from last sle for the same item and warehouse
	if not company:
		company = erpnext.get_default_company()

	last_valuation_rate = frappe.db.sql("""select valuation_rate
		from `tabStock Ledger Entry`
		where
			item_code = %s
			AND warehouse = %s
			AND valuation_rate >= 0
			AND NOT (voucher_no = %s AND voucher_type = %s)
		order by posting_date desc, posting_time desc, name desc limit 1""", (item_code, warehouse, voucher_no, voucher_type))

	if not last_valuation_rate:
		# Get valuation rate from last sle for the item against any warehouse
		last_valuation_rate = frappe.db.sql("""select valuation_rate
			from `tabStock Ledger Entry`
			where
				item_code = %s
				AND valuation_rate > 0
				AND NOT(voucher_no = %s AND voucher_type = %s)
			order by posting_date desc, posting_time desc, name desc limit 1""", (item_code, voucher_no, voucher_type))

	if last_valuation_rate:
		return flt(last_valuation_rate[0][0])

	# If negative stock allowed, and item delivered without any incoming entry,
	# system does not found any SLE, then take valuation rate from Item
	valuation_rate = frappe.db.get_value("Item", item_code, "valuation_rate")

	if not valuation_rate:
		# try Item Standard rate
		valuation_rate = frappe.db.get_value("Item", item_code, "standard_rate")

		if not valuation_rate:
			# try in price list
			valuation_rate = frappe.db.get_value('Item Price',
				dict(item_code=item_code, buying=1, currency=currency),
				'price_list_rate')

	if not allow_zero_rate and not valuation_rate and raise_error_if_no_rate \
			and cint(erpnext.is_perpetual_inventory_enabled(company)):
		frappe.local.message_log = []
		form_link = frappe.utils.get_link_to_form("Item", item_code)

		message = _("Valuation Rate for the Item {0}, is required to do accounting entries for {1} {2}.").format(form_link, voucher_type, voucher_no)
		message += "<br><br>" + _(" Here are the options to proceed:")
		solutions = "<li>" + _("If the item is transacting as a Zero Valuation Rate item in this entry, please enable 'Allow Zero Valuation Rate' in the {0} Item table.").format(voucher_type) + "</li>"
		solutions += "<li>" + _("If not, you can Cancel / Submit this entry ") + _("{0}").format(frappe.bold("after")) + _(" performing either one below:") + "</li>"
		sub_solutions = "<ul><li>" + _("Create an incoming stock transaction for the Item.") + "</li>"
		sub_solutions += "<li>" + _("Mention Valuation Rate in the Item master.") + "</li></ul>"
		msg = message + solutions + sub_solutions + "</li>"

		frappe.throw(msg=msg, title=_("Valuation Rate Missing"))

	return valuation_rate

def update_qty_in_future_sle(args, allow_negative_stock=None):
	frappe.db.sql("""
		update `tabStock Ledger Entry`
		set qty_after_transaction = qty_after_transaction + {qty}
		where
			item_code = %(item_code)s
			and warehouse = %(warehouse)s
			and voucher_no != %(voucher_no)s
			and is_cancelled = 0
			and (timestamp(posting_date, posting_time) > timestamp(%(posting_date)s, %(posting_time)s)
				or (
					timestamp(posting_date, posting_time) = timestamp(%(posting_date)s, %(posting_time)s)
					and creation > %(creation)s
				)
			)
	""".format(qty=args.actual_qty), args)

	validate_negative_qty_in_future_sle(args, allow_negative_stock)

def validate_negative_qty_in_future_sle(args, allow_negative_stock=None):
	allow_negative_stock = allow_negative_stock \
		or cint(frappe.db.get_single_value("Stock Settings", "allow_negative_stock"))

	if args.actual_qty < 0 and not allow_negative_stock:
		sle = get_future_sle_with_negative_qty(args)
		if sle:
			message = _("{0} units of {1} needed in {2} on {3} {4} for {5} to complete this transaction.").format(
				abs(sle[0]["qty_after_transaction"]),
				frappe.get_desk_link('Item', args.item_code),
				frappe.get_desk_link('Warehouse', args.warehouse),
				sle[0]["posting_date"], sle[0]["posting_time"],
				frappe.get_desk_link(sle[0]["voucher_type"], sle[0]["voucher_no"]))

			frappe.throw(message, NegativeStockError, title='Insufficient Stock')

def get_future_sle_with_negative_qty(args):
	return frappe.db.sql("""
		select
			qty_after_transaction, posting_date, posting_time,
			voucher_type, voucher_no
		from `tabStock Ledger Entry`
		where
			item_code = %(item_code)s
			and warehouse = %(warehouse)s
			and voucher_no != %(voucher_no)s
			and timestamp(posting_date, posting_time) >= timestamp(%(posting_date)s, %(posting_time)s)
			and is_cancelled = 0
			and qty_after_transaction < 0
		order by timestamp(posting_date, posting_time) asc
		limit 1
	""", args, as_dict=1)