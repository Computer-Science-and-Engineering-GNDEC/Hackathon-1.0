QUnit.test("Test: Company", function (assert) {
	assert.expect(0);

	let done = assert.async();

	frappe.run_serially([
		// Added company for Work Order testing
		() => frappe.set_route("List", "Company"),
		() => frappe.new_doc("Company"),
		() => frappe.timeout(1),
		() => cur_frm.set_value("company_name", "For Testing"),
		() => cur_frm.set_value("abbr", "RB"),
		() => cur_frm.set_value("default_currency", "INR"),
		() => cur_frm.save(),
		() => frappe.timeout(1),

		() => done()
	]);
});