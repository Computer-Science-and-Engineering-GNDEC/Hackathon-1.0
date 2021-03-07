// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.ui.form.on("Expense Claim Type", {
	refresh: function(frm) {
		frm.fields_dict["accounts"].grid.get_field("default_account").get_query = function(doc, cdt, cdn) {
			var d = locals[cdt][cdn];
			return {
				filters: {
					"is_group": 0,
					"root_type": frm.doc.deferred_expense_account ? "Asset" : "Expense",
					'company': d.company
				}
			}
		}
	}
})
