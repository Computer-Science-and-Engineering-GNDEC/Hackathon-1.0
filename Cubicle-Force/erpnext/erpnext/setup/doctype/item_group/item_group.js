// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.ui.form.on("Item Group", {
	onload: function(frm) {
		frm.list_route = "Tree/Item Group";

		//get query select item group
		frm.fields_dict['parent_item_group'].get_query = function(doc,cdt,cdn) {
			return{
				filters:[
					['Item Group', 'is_group', '=', 1],
					['Item Group', 'name', '!=', doc.item_group_name]
				]
			}
		}
		frm.fields_dict["item_group_defaults"].grid.get_field("expense_account").get_query = function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "erpnext.controllers.queries.get_expense_account",
				filters: { company: row.company }
			}
		}
		frm.fields_dict["item_group_defaults"].grid.get_field("income_account").get_query = function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "erpnext.controllers.queries.get_income_account",
				filters: { company: row.company }
			}
		}

		frm.fields_dict["item_group_defaults"].grid.get_field("buying_cost_center").get_query = function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				filters: {
					"is_group": 0,
					"company": row.company
				}
			}
		}

		frm.fields_dict["item_group_defaults"].grid.get_field("selling_cost_center").get_query = function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				filters: {
					"is_group": 0,
					"company": row.company
				}
			}
		}
	},

	refresh: function(frm) {
		frm.trigger("set_root_readonly");
		frm.add_custom_button(__("Item Group Tree"), function() {
			frappe.set_route("Tree", "Item Group");
		});

		if(!frm.is_new()) {
			frm.add_custom_button(__("Items"), function() {
				frappe.set_route("List", "Item", {"item_group": frm.doc.name});
			});
		}
		
		frappe.model.with_doctype('Item', () => {
			const item_meta = frappe.get_meta('Item');

			const valid_fields = item_meta.fields.filter(
				df => ['Link', 'Table MultiSelect'].includes(df.fieldtype) && !df.hidden
			).map(df => ({ label: df.label, value: df.fieldname }));

			const field = frappe.meta.get_docfield("Website Filter Field", "fieldname", frm.docname);
			field.fieldtype = 'Select';
			field.options = valid_fields;
			frm.fields_dict.filter_fields.grid.refresh();
		});
	},

	set_root_readonly: function(frm) {
		// read-only for root item group
		frm.set_intro("");
		if(!frm.doc.parent_item_group && !frm.doc.__islocal) {
			frm.set_read_only();
			frm.set_intro(__("This is a root item group and cannot be edited."), true);
		}
	},

	page_name: frappe.utils.warn_page_name_change
});
