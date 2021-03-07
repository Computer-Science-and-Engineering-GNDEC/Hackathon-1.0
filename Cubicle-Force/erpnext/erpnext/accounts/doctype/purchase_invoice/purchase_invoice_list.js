// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// render
frappe.listview_settings['Purchase Invoice'] = {
	add_fields: ["supplier", "supplier_name", "base_grand_total", "outstanding_amount", "due_date", "company",
		"currency", "is_return", "release_date", "on_hold", "represents_company", "is_internal_supplier"],
	get_indicator: function(doc) {
		if ((flt(doc.outstanding_amount) <= 0) && doc.docstatus == 1 &&  doc.status == 'Debit Note Issued') {
			return [__("Debit Note Issued"), "darkgrey", "outstanding_amount,<=,0"];
		} else if (flt(doc.outstanding_amount) > 0 && doc.docstatus==1) {
			if(cint(doc.on_hold) && !doc.release_date) {
				return [__("On Hold"), "darkgrey"];
			} else if (cint(doc.on_hold) && doc.release_date && frappe.datetime.get_diff(doc.release_date, frappe.datetime.nowdate()) > 0) {
				return [__("Temporarily on Hold"), "darkgrey"];
			} else if (frappe.datetime.get_diff(doc.due_date) < 0) {
				return [__("Overdue"), "red", "outstanding_amount,>,0|due_date,<,Today"];
			} else {
				return [__("Unpaid"), "orange", "outstanding_amount,>,0|due_date,>=,Today"];
			}
		} else if (cint(doc.is_return)) {
			return [__("Return"), "gray", "is_return,=,Yes"];
		} else if (doc.company == doc.represents_company && doc.is_internal_supplier) {
			return [__("Internal Transfer"), "darkgrey", "outstanding_amount,=,0"];
		} else if (flt(doc.outstanding_amount)==0 && doc.docstatus==1) {
			return [__("Paid"), "green", "outstanding_amount,=,0"];
		}
	}
};