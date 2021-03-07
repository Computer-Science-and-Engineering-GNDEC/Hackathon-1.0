// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Student Admission', {
	program: function(frm) {
		if (frm.doc.academic_year && frm.doc.program) {
			frm.doc.route = frappe.model.scrub(frm.doc.program) + "-" + frappe.model.scrub(frm.doc.academic_year)
			frm.refresh_field("route");
		}
	},

	academic_year: function(frm) {
		frm.trigger("program");
	},

	admission_end_date: function(frm) {
		if(frm.doc.admission_end_date && frm.doc.admission_end_date <= frm.doc.admission_start_date){
			frm.set_value("admission_end_date", "");
			frappe.throw(__("Admission End Date should be greater than Admission Start Date."));
		}
	}
});
