// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide("erpnext.bom");

frappe.ui.form.on("BOM", {
	setup: function(frm) {
		frm.custom_make_buttons = {
			'Work Order': 'Work Order',
			'Quality Inspection': 'Quality Inspection'
		};

		frm.set_query("bom_no", "items", function() {
			return {
				filters: {
					'currency': frm.doc.currency,
					'company': frm.doc.company
				}
			};
		});

		frm.set_query("source_warehouse", "items", function() {
			return {
				filters: {
					'company': frm.doc.company
				}
			};
		});

		frm.set_query("item", function() {
			return {
				query: "erpnext.manufacturing.doctype.bom.bom.item_query"
			};
		});

		frm.set_query("project", function() {
			return{
				filters:[
					['Project', 'status', 'not in', 'Completed, Cancelled']
				]
			};
		});

		frm.set_query("item_code", "items", function(doc) {
			return {
				query: "erpnext.manufacturing.doctype.bom.bom.item_query",
				filters: {
					"item_code": doc.item
				}
			};
		});

		frm.set_query("bom_no", "items", function(doc, cdt, cdn) {
			var d = locals[cdt][cdn];
			return {
				filters: {
					'item': d.item_code,
					'is_active': 1,
					'docstatus': 1
				}
			};
		});
	},

	onload_post_render: function(frm) {
		frm.get_field("items").grid.set_multiple_add("item_code", "qty");
	},

	refresh: function(frm) {
		frm.toggle_enable("item", frm.doc.__islocal);
		toggle_operations(frm);

		frm.set_indicator_formatter('item_code',
			function(doc) {
				if (doc.original_item){
					return (doc.item_code != doc.original_item) ? "orange" : ""
				}
				return ""
			}
		)

		if (!frm.doc.__islocal && frm.doc.docstatus<2) {
			frm.add_custom_button(__("Update Cost"), function() {
				frm.events.update_cost(frm);
			});
			frm.add_custom_button(__("Browse BOM"), function() {
				frappe.route_options = {
					"bom": frm.doc.name
				};
				frappe.set_route("Tree", "BOM");
			});
		}

		if(frm.doc.docstatus!=0) {
			frm.add_custom_button(__("Work Order"), function() {
				frm.trigger("make_work_order");
			}, __("Create"));

			if (frm.doc.has_variants) {
				frm.add_custom_button(__("Variant BOM"), function() {
					frm.trigger("make_variant_bom");
				}, __("Create"));
			}

			if (frm.doc.inspection_required) {
				frm.add_custom_button(__("Quality Inspection"), function() {
					frm.trigger("make_quality_inspection");
				}, __("Create"));
			}

			frm.page.set_inner_btn_group_as_primary(__('Create'));
		}

		if(frm.doc.items && frm.doc.allow_alternative_item) {
			const has_alternative = frm.doc.items.find(i => i.allow_alternative_item === 1);
			if (frm.doc.docstatus == 0 && has_alternative) {
				frm.add_custom_button(__('Alternate Item'), () => {
					erpnext.utils.select_alternate_items({
						frm: frm,
						child_docname: "items",
						warehouse_field: "source_warehouse",
						child_doctype: "BOM Item",
						original_item_field: "original_item",
						condition: (d) => {
							if (d.allow_alternative_item) {return true;}
						}
					})
				});
			}
		}


		if (frm.doc.has_variants) {
			frm.set_intro(__('This is a Template BOM and will be used to make the work order for {0} of the item {1}',
				[
					`<a class="variants-intro">variants</a>`,
					`<a href="/app/item/${frm.doc.item}">${frm.doc.item}</a>`,
				]), true);

			frm.$wrapper.find(".variants-intro").on("click", () => {
				frappe.set_route("List", "Item", {"variant_of": frm.doc.item});
			});
		}
	},

	make_work_order: function(frm) {
		frm.events.setup_variant_prompt(frm, "Work Order", (frm, item, data, variant_items) => {
			frappe.call({
				method: "erpnext.manufacturing.doctype.work_order.work_order.make_work_order",
				args: {
					bom_no: frm.doc.name,
					item: item,
					qty: data.qty || 0.0,
					project: frm.doc.project,
					variant_items: variant_items
				},
				freeze: true,
				callback: function(r) {
					if(r.message) {
						let doc = frappe.model.sync(r.message)[0];
						frappe.set_route("Form", doc.doctype, doc.name);
					}
				}
			});
		});
	},

	make_variant_bom: function(frm) {
		frm.events.setup_variant_prompt(frm, "Variant BOM", (frm, item, data, variant_items) => {
			frappe.call({
				method: "erpnext.manufacturing.doctype.bom.bom.make_variant_bom",
				args: {
					source_name: frm.doc.name,
					bom_no: frm.doc.name,
					item: item,
					variant_items: variant_items
				},
				freeze: true,
				callback: function(r) {
					if(r.message) {
						let doc = frappe.model.sync(r.message)[0];
						frappe.set_route("Form", doc.doctype, doc.name);
					}
				}
			});
		}, true);
	},

	setup_variant_prompt: function(frm, title, callback, skip_qty_field) {
		const fields = [];

		if (frm.doc.has_variants) {
			fields.push({
				fieldtype: 'Link',
				label: __('Variant Item'),
				fieldname: 'item',
				options: "Item",
				reqd: 1,
				get_query: function() {
					return {
						query: "erpnext.controllers.queries.item_query",
						filters: {
							"variant_of": frm.doc.item
						}
					};
				}
			});
		}

		if (!skip_qty_field) {
			fields.push({
				fieldtype: 'Float',
				label: __('Qty To Manufacture'),
				fieldname: 'qty',
				reqd: 1,
				default: 1
			});
		}

		var has_template_rm = frm.doc.items.filter(d => d.has_variants === 1) || [];
		if (has_template_rm && has_template_rm.length > 0) {
			fields.push({
				fieldname: "items",
				fieldtype: "Table",
				label: __("Raw Materials"),
				fields: [
					{
						fieldname: "item_code",
						options: "Item",
						label: __("Template Item"),
						fieldtype: "Link",
						in_list_view: 1,
						reqd: 1,
					},
					{
						fieldname: "varint_item_code",
						options: "Item",
						label: __("Variant Item"),
						fieldtype: "Link",
						in_list_view: 1,
						reqd: 1,
						get_query: function(data) {
							if (!data.item_code) {
								frappe.throw(__("Select template item"));
							}

							return {
								query: "erpnext.controllers.queries.item_query",
								filters: {
									"variant_of": data.item_code
								}
							};
						}
					},
					{
						fieldname: "qty",
						label: __("Quantity"),
						fieldtype: "Float",
						in_list_view: 1,
						reqd: 1,
					},
					{
						fieldname: "source_warehouse",
						label: __("Source Warehouse"),
						fieldtype: "Link",
						options: "Warehouse"
					},
					{
						fieldname: "operation",
						label: __("Operation"),
						fieldtype: "Data",
						hidden: 1,
					}
				],
				in_place_edit: true,
				data: [],
				get_data: function () {
					return [];
				},
			});
		}

		let dialog = frappe.prompt(fields, data => {
			let item = data.item || frm.doc.item;
			let variant_items = data.items || [];

			variant_items.forEach(d => {
				if (!d.varint_item_code) {
					frappe.throw(__("Select variant item code for the template item {0}", [d.item_code]));
				}
			})

			callback(frm, item, data, variant_items);

		}, __(title), __("Create"));

		has_template_rm.forEach(d => {
			dialog.fields_dict.items.df.data.push({
				"item_code": d.item_code,
				"varint_item_code": "",
				"qty": d.qty,
				"source_warehouse": d.source_warehouse,
				"operation": d.operation
			});
		});

		if (has_template_rm) {
			dialog.fields_dict.items.grid.refresh();
		}
	},

	make_quality_inspection: function(frm) {
		frappe.model.open_mapped_doc({
			method: "erpnext.stock.doctype.quality_inspection.quality_inspection.make_quality_inspection",
			frm: frm
		})
	},

	update_cost: function(frm) {
		return frappe.call({
			doc: frm.doc,
			method: "update_cost",
			freeze: true,
			args: {
				update_parent: true,
				from_child_bom:false,
				save: frm.doc.docstatus === 1 ? true : false
			},
			callback: function(r) {
				refresh_field("items");
				if(!r.exc) frm.refresh_fields();
			}
		});
	},

	rm_cost_as_per: function(frm) {
		if (in_list(["Valuation Rate", "Last Purchase Rate"], frm.doc.rm_cost_as_per)) {
			frm.set_value("plc_conversion_rate", 1.0);
		}
	},

	routing: function(frm) {
		if (frm.doc.routing) {
			frappe.call({
				doc: frm.doc,
				method: "get_routing",
				freeze: true,
				callback: function(r) {
					if (!r.exc) {
						frm.refresh_fields();
						erpnext.bom.calculate_op_cost(frm.doc);
						erpnext.bom.calculate_total(frm.doc);
					}
				}
			});
		}
	}
});

erpnext.bom.BomController = erpnext.TransactionController.extend({
	conversion_rate: function(doc) {
		if(this.frm.doc.currency === this.get_company_currency()) {
			this.frm.set_value("conversion_rate", 1.0);
		} else {
			erpnext.bom.update_cost(doc);
		}
	},

	item_code: function(doc, cdt, cdn){
		var scrap_items = false;
		var child = locals[cdt][cdn];
		if (child.doctype == 'BOM Scrap Item') {
			scrap_items = true;
		}

		if (child.bom_no) {
			child.bom_no = '';
		}

		get_bom_material_detail(doc, cdt, cdn, scrap_items);
	},

	buying_price_list: function(doc) {
		this.apply_price_list();
	},

	plc_conversion_rate: function(doc) {
		if (!this.in_apply_price_list) {
			this.apply_price_list(null, true);
		}
	},

	conversion_factor: function(doc, cdt, cdn) {
		if (frappe.meta.get_docfield(cdt, "stock_qty", cdn)) {
			var item = frappe.get_doc(cdt, cdn);
			frappe.model.round_floats_in(item, ["qty", "conversion_factor"]);
			item.stock_qty = flt(item.qty * item.conversion_factor, precision("stock_qty", item));
			refresh_field("stock_qty", item.name, item.parentfield);
			this.toggle_conversion_factor(item);
			this.frm.events.update_cost(this.frm);
		}
	},
});

$.extend(cur_frm.cscript, new erpnext.bom.BomController({frm: cur_frm}));

cur_frm.cscript.hour_rate = function(doc) {
	erpnext.bom.calculate_op_cost(doc);
	erpnext.bom.calculate_total(doc);
};

cur_frm.cscript.time_in_mins = cur_frm.cscript.hour_rate;

cur_frm.cscript.bom_no = function(doc, cdt, cdn) {
	get_bom_material_detail(doc, cdt, cdn, false);
};

cur_frm.cscript.is_default = function(doc) {
	if (doc.is_default) cur_frm.set_value("is_active", 1);
};

var get_bom_material_detail = function(doc, cdt, cdn, scrap_items) {
	if (!doc.company) {
		frappe.throw({message: __("Please select a Company first."), title: __("Mandatory")});
	}

	var d = locals[cdt][cdn];
	if (d.item_code) {
		return frappe.call({
			doc: doc,
			method: "get_bom_material_detail",
			args: {
				"company": doc.company,
				"item_code": d.item_code,
				"bom_no": d.bom_no != null ? d.bom_no: '',
				"scrap_items": scrap_items,
				"qty": d.qty,
				"stock_qty": d.stock_qty,
				"include_item_in_manufacturing": d.include_item_in_manufacturing,
				"uom": d.uom,
				"stock_uom": d.stock_uom,
				"conversion_factor": d.conversion_factor,
				"sourced_by_supplier": d.sourced_by_supplier
			},
			callback: function(r) {
				d = locals[cdt][cdn];
				$.extend(d, r.message);
				refresh_field("items");
				refresh_field("scrap_items");

				doc = locals[doc.doctype][doc.name];
				erpnext.bom.calculate_rm_cost(doc);
				erpnext.bom.calculate_scrap_materials_cost(doc);
				erpnext.bom.calculate_total(doc);
			},
			freeze: true
		});
	}
};

cur_frm.cscript.qty = function(doc) {
	erpnext.bom.calculate_rm_cost(doc);
	erpnext.bom.calculate_scrap_materials_cost(doc);
	erpnext.bom.calculate_total(doc);
};

cur_frm.cscript.rate = function(doc, cdt, cdn) {
	var d = locals[cdt][cdn];
	var scrap_items = false;

	if(cdt == 'BOM Scrap Item') {
		scrap_items = true;
	}

	if (d.bom_no) {
		frappe.msgprint(__("You cannot change the rate if BOM is mentioned against any Item."));
		get_bom_material_detail(doc, cdt, cdn, scrap_items);
	} else {
		erpnext.bom.calculate_rm_cost(doc);
		erpnext.bom.calculate_scrap_materials_cost(doc);
		erpnext.bom.calculate_total(doc);
	}
};

erpnext.bom.update_cost = function(doc) {
	erpnext.bom.calculate_op_cost(doc);
	erpnext.bom.calculate_rm_cost(doc);
	erpnext.bom.calculate_scrap_materials_cost(doc);
	erpnext.bom.calculate_total(doc);
};

erpnext.bom.calculate_op_cost = function(doc) {
	var op = doc.operations || [];
	doc.operating_cost = 0.0;
	doc.base_operating_cost = 0.0;

	for(var i=0;i<op.length;i++) {
		var operating_cost = flt(flt(op[i].hour_rate) * flt(op[i].time_in_mins) / 60, 2);
		var base_operating_cost = flt(operating_cost * doc.conversion_rate, 2);
		frappe.model.set_value('BOM Operation',op[i].name, "operating_cost", operating_cost);
		frappe.model.set_value('BOM Operation',op[i].name, "base_operating_cost", base_operating_cost);

		doc.operating_cost += operating_cost;
		doc.base_operating_cost += base_operating_cost;
	}
	refresh_field(['operating_cost', 'base_operating_cost']);
};

// rm : raw material
erpnext.bom.calculate_rm_cost = function(doc) {
	var rm = doc.items || [];
	var total_rm_cost = 0;
	var base_total_rm_cost = 0;
	for(var i=0;i<rm.length;i++) {
		var amount = flt(rm[i].rate) * flt(rm[i].qty);
		var base_amount = amount * flt(doc.conversion_rate);

		frappe.model.set_value('BOM Item', rm[i].name, 'base_rate',
			flt(rm[i].rate) * flt(doc.conversion_rate));
		frappe.model.set_value('BOM Item', rm[i].name, 'amount', amount);
		frappe.model.set_value('BOM Item', rm[i].name, 'base_amount', base_amount);
		frappe.model.set_value('BOM Item', rm[i].name,
			'qty_consumed_per_unit', flt(rm[i].stock_qty)/flt(doc.quantity));

		total_rm_cost += amount;
		base_total_rm_cost += base_amount;
	}
	cur_frm.set_value("raw_material_cost", total_rm_cost);
	cur_frm.set_value("base_raw_material_cost", base_total_rm_cost);
};

// sm : scrap material
erpnext.bom.calculate_scrap_materials_cost = function(doc) {
	var sm = doc.scrap_items || [];
	var total_sm_cost = 0;
	var base_total_sm_cost = 0;

	for(var i=0;i<sm.length;i++) {
		var base_rate = flt(sm[i].rate) * flt(doc.conversion_rate);
		var amount = flt(sm[i].rate) * flt(sm[i].stock_qty);
		var base_amount = amount * flt(doc.conversion_rate);

		frappe.model.set_value('BOM Scrap Item',sm[i].name, 'base_rate', base_rate);
		frappe.model.set_value('BOM Scrap Item',sm[i].name, 'amount', amount);
		frappe.model.set_value('BOM Scrap Item',sm[i].name, 'base_amount', base_amount);

		total_sm_cost += amount;
		base_total_sm_cost += base_amount;
	}

	cur_frm.set_value("scrap_material_cost", total_sm_cost);
	cur_frm.set_value("base_scrap_material_cost", base_total_sm_cost);
};

// Calculate Total Cost
erpnext.bom.calculate_total = function(doc) {
	var total_cost = flt(doc.operating_cost) + flt(doc.raw_material_cost) - flt(doc.scrap_material_cost);
	var base_total_cost = flt(doc.base_operating_cost) + flt(doc.base_raw_material_cost)
		- flt(doc.base_scrap_material_cost);

	cur_frm.set_value("total_cost", total_cost);
	cur_frm.set_value("base_total_cost", base_total_cost);
};

cur_frm.cscript.validate = function(doc) {
	erpnext.bom.update_cost(doc);
};

frappe.ui.form.on("BOM Operation", "operation", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];

	if(!d.operation) return;

	frappe.call({
		"method": "frappe.client.get",
		args: {
			doctype: "Operation",
			name: d.operation
		},
		callback: function (data) {
			if(data.message.description) {
				frappe.model.set_value(d.doctype, d.name, "description", data.message.description);
			}
			if(data.message.workstation) {
				frappe.model.set_value(d.doctype, d.name, "workstation", data.message.workstation);
			}
		}
	});
});

frappe.ui.form.on("BOM Operation", "workstation", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];

	frappe.call({
		"method": "frappe.client.get",
		args: {
			doctype: "Workstation",
			name: d.workstation
		},
		callback: function (data) {
			frappe.model.set_value(d.doctype, d.name, "base_hour_rate", data.message.hour_rate);
			frappe.model.set_value(d.doctype, d.name, "hour_rate",
				flt(flt(data.message.hour_rate) / flt(frm.doc.conversion_rate)), 2);

			erpnext.bom.calculate_op_cost(frm.doc);
			erpnext.bom.calculate_total(frm.doc);
		}
	});
});

frappe.ui.form.on("BOM Item", "qty", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	d.stock_qty = d.qty * d.conversion_factor;
	refresh_field("stock_qty", d.name, d.parentfield);
});

frappe.ui.form.on("BOM Item", "item_code", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.db.get_value('Item', {name: d.item_code}, 'allow_alternative_item', (r) => {
		d.allow_alternative_item = r.allow_alternative_item
	})
	refresh_field("allow_alternative_item", d.name, d.parentfield);
});

frappe.ui.form.on("BOM Item", "sourced_by_supplier", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	if (d.sourced_by_supplier) {
		d.rate = 0;
		refresh_field("rate", d.name, d.parentfield);
	}
});

frappe.ui.form.on("BOM Item", "rate", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	if (d.sourced_by_supplier) {
		d.rate = 0;
		refresh_field("rate", d.name, d.parentfield);
	}
});

frappe.ui.form.on("BOM Operation", "operations_remove", function(frm) {
	erpnext.bom.calculate_op_cost(frm.doc);
	erpnext.bom.calculate_total(frm.doc);
});

frappe.ui.form.on("BOM Item", "items_remove", function(frm) {
	erpnext.bom.calculate_rm_cost(frm.doc);
	erpnext.bom.calculate_total(frm.doc);
});

var toggle_operations = function(frm) {
	frm.toggle_display("operations_section", cint(frm.doc.with_operations) == 1);
	frm.toggle_display("transfer_material_against", cint(frm.doc.with_operations) == 1);
	frm.toggle_reqd("transfer_material_against", cint(frm.doc.with_operations) == 1);
};

frappe.ui.form.on("BOM", "with_operations", function(frm) {
	if(!cint(frm.doc.with_operations)) {
		frm.set_value("operations", []);
	}
	toggle_operations(frm);
});