QUnit.module('Sales Order');

QUnit.test("test sales order", function(assert) {
	assert.expect(12);
	let done = assert.async();
	frappe.run_serially([
		() => {
			return frappe.tests.make('Sales Order', [
				{customer: 'Test Customer 1'},
				{items: [
					[
						{'delivery_date': frappe.datetime.add_days(frappe.defaults.get_default("year_end_date"), 1)},
						{'qty': 5.123},
						{'item_code': 'Test Product 3'},
					]
				]},
				{customer_address: 'Test1-Billing'},
				{shipping_address_name: 'Test1-Shipping'},
				{contact_person: 'Contact 1-Test Customer 1'},
				{taxes_and_charges: 'TEST In State GST - FT'},
				{tc_name: 'Test Term 1'},
				{terms: 'This is Test'},
				{payment_terms_template: '_Test Payment Term Template UI'}
			]);
		},
		() => {
			return frappe.tests.set_form_values(cur_frm, [
				{selling_price_list:'Test-Selling-USD'},
				{currency: 'USD'}
			]);
		},
		() => frappe.timeout(1.5),
		() => {
			// get_item_details
			assert.ok(cur_frm.doc.items[0].item_name=='Test Product 3', "Item name correct");
			// get tax details
			assert.ok(cur_frm.doc.taxes_and_charges=='TEST In State GST - FT', "Tax details correct");
			// get tax account head details
			assert.ok(cur_frm.doc.taxes[0].account_head=='CGST - '+frappe.get_abbr(frappe.defaults.get_default('Company')), " Account Head abbr correct");
		},
		() => cur_frm.save(),
		() => frappe.timeout(1),
		() => cur_frm.print_doc(),
		() => frappe.timeout(1),
		() => {
			// Payment Terms
			assert.ok(cur_frm.doc.payment_terms_template, "Payment Terms Template is correct");
			assert.ok(cur_frm.doc.payment_schedule.length > 0, "Payment Term Schedule is not empty");

			// totals
			assert.ok(cur_frm.doc.items[0].price_list_rate==250, "Item 1 price_list_rate");
			assert.ok(cur_frm.doc.net_total== 1280.75, "net total correct ");
			assert.ok(cur_frm.doc.base_grand_total== flt(1511.29* cur_frm.doc.conversion_rate, precision('base_grand_total')), String(flt(1511.29* cur_frm.doc.conversion_rate, precision('base_grand_total')) + ' ' + cur_frm.doc.base_grand_total));
			assert.ok(cur_frm.doc.grand_total== 1511.29 , "grand total correct ");
			assert.ok(cur_frm.doc.rounded_total== 1511.30, "rounded total correct ");

			// print format
			assert.ok($('.btn-print-print').is(':visible'), "Print Format Available");
			frappe.timeout(1);
			assert.ok($(".section-break+ .section-break .column-break:nth-child(1) .data-field:nth-child(1) .value").text().includes("Billing Street 1"), "Print Preview Works As Expected");
		},
		() => cur_frm.print_doc(),
		() => frappe.tests.click_button('Submit'),
		() => frappe.tests.click_button('Yes'),
		() => frappe.timeout(0.3),
		() => done()
	]);
});
