import traceback

import taxjar

import frappe
from erpnext import get_default_company
from frappe import _
from frappe.contacts.doctype.address.address import get_company_address

TAX_ACCOUNT_HEAD = frappe.db.get_single_value("TaxJar Settings", "tax_account_head")
SHIP_ACCOUNT_HEAD = frappe.db.get_single_value("TaxJar Settings", "shipping_account_head")
TAXJAR_CREATE_TRANSACTIONS = frappe.db.get_single_value("TaxJar Settings", "taxjar_create_transactions")
TAXJAR_CALCULATE_TAX = frappe.db.get_single_value("TaxJar Settings", "taxjar_calculate_tax")
SUPPORTED_COUNTRY_CODES = ["AT", "AU", "BE", "BG", "CA", "CY", "CZ", "DE", "DK", "EE", "ES", "FI",
	"FR", "GB", "GR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO",
	"SE", "SI", "SK", "US"]


def get_client():
	taxjar_settings = frappe.get_single("TaxJar Settings")

	if not taxjar_settings.is_sandbox:
		api_key = taxjar_settings.api_key and taxjar_settings.get_password("api_key")
		api_url = taxjar.DEFAULT_API_URL
	else:
		api_key = taxjar_settings.sandbox_api_key and taxjar_settings.get_password("sandbox_api_key")
		api_url = taxjar.SANDBOX_API_URL

	if api_key and api_url:
		return taxjar.Client(api_key=api_key, api_url=api_url)


def create_transaction(doc, method):
	"""Create an order transaction in TaxJar"""

	if not TAXJAR_CREATE_TRANSACTIONS:
		return

	client = get_client()

	if not client:
		return

	sales_tax = sum([tax.tax_amount for tax in doc.taxes if tax.account_head == TAX_ACCOUNT_HEAD])

	if not sales_tax:
		return

	tax_dict = get_tax_data(doc)

	if not tax_dict:
		return

	tax_dict['transaction_id'] = doc.name
	tax_dict['transaction_date'] = frappe.utils.today()
	tax_dict['sales_tax'] = sales_tax
	tax_dict['amount'] = doc.total + tax_dict['shipping']

	try:
		client.create_order(tax_dict)
	except taxjar.exceptions.TaxJarResponseError as err:
		frappe.throw(_(sanitize_error_response(err)))
	except Exception as ex:
		print(traceback.format_exc(ex))


def delete_transaction(doc, method):
	"""Delete an existing TaxJar order transaction"""

	if not TAXJAR_CREATE_TRANSACTIONS:
		return

	client = get_client()

	if not client:
		return

	client.delete_order(doc.name)


def get_tax_data(doc):
	from_address = get_company_address_details(doc)
	from_shipping_state = from_address.get("state")
	from_country_code = frappe.db.get_value("Country", from_address.country, "code")
	from_country_code = from_country_code.upper()

	to_address = get_shipping_address_details(doc)
	to_shipping_state = to_address.get("state")
	to_country_code = frappe.db.get_value("Country", to_address.country, "code")
	to_country_code = to_country_code.upper()

	if to_country_code not in SUPPORTED_COUNTRY_CODES:
		return

	shipping = sum([tax.tax_amount for tax in doc.taxes if tax.account_head == SHIP_ACCOUNT_HEAD])

	if to_shipping_state is not None:
		to_shipping_state = get_iso_3166_2_state_code(to_address)

	tax_dict = {
		'from_country': from_country_code,
		'from_zip': from_address.pincode,
		'from_state': from_shipping_state,
		'from_city': from_address.city,
		'from_street': from_address.address_line1,
		'to_country': to_country_code,
		'to_zip': to_address.pincode,
		'to_city': to_address.city,
		'to_street': to_address.address_line1,
		'to_state': to_shipping_state,
		'shipping': shipping,
		'amount': doc.net_total
	}

	return tax_dict


def set_sales_tax(doc, method):
	if not TAXJAR_CALCULATE_TAX:
		return

	if not doc.items:
		return

	# if the party is exempt from sales tax, then set all tax account heads to zero
	sales_tax_exempted = hasattr(doc, "exempt_from_sales_tax") and doc.exempt_from_sales_tax \
		or frappe.db.has_column("Customer", "exempt_from_sales_tax") and frappe.db.get_value("Customer", doc.customer, "exempt_from_sales_tax")

	if sales_tax_exempted:
		for tax in doc.taxes:
			if tax.account_head == TAX_ACCOUNT_HEAD:
				tax.tax_amount = 0
				break

		doc.run_method("calculate_taxes_and_totals")
		return

	tax_dict = get_tax_data(doc)

	if not tax_dict:
		# Remove existing tax rows if address is changed from a taxable state/country
		setattr(doc, "taxes", [tax for tax in doc.taxes if tax.account_head != TAX_ACCOUNT_HEAD])
		return

	tax_data = validate_tax_request(tax_dict)

	if tax_data is not None:
		if not tax_data.amount_to_collect:
			setattr(doc, "taxes", [tax for tax in doc.taxes if tax.account_head != TAX_ACCOUNT_HEAD])
		elif tax_data.amount_to_collect > 0:
			# Loop through tax rows for existing Sales Tax entry
			# If none are found, add a row with the tax amount
			for tax in doc.taxes:
				if tax.account_head == TAX_ACCOUNT_HEAD:
					tax.tax_amount = tax_data.amount_to_collect

					doc.run_method("calculate_taxes_and_totals")
					break
			else:
				doc.append("taxes", {
					"charge_type": "Actual",
					"description": "Sales Tax",
					"account_head": TAX_ACCOUNT_HEAD,
					"tax_amount": tax_data.amount_to_collect
				})

			doc.run_method("calculate_taxes_and_totals")


def validate_tax_request(tax_dict):
	"""Return the sales tax that should be collected for a given order."""

	client = get_client()

	if not client:
		return

	try:
		tax_data = client.tax_for_order(tax_dict)
	except taxjar.exceptions.TaxJarResponseError as err:
		frappe.throw(_(sanitize_error_response(err)))
	else:
		return tax_data


def get_company_address_details(doc):
	"""Return default company address details"""

	company_address = get_company_address(get_default_company()).company_address

	if not company_address:
		frappe.throw(_("Please set a default company address"))

	company_address = frappe.get_doc("Address", company_address)
	return company_address


def get_shipping_address_details(doc):
	"""Return customer shipping address details"""

	if doc.shipping_address_name:
		shipping_address = frappe.get_doc("Address", doc.shipping_address_name)
	else:
		shipping_address = get_company_address_details(doc)

	return shipping_address


def get_iso_3166_2_state_code(address):
	import pycountry
	country_code = frappe.db.get_value("Country", address.get("country"), "code")

	error_message = _("""{0} is not a valid state! Check for typos or enter the ISO code for your state.""").format(address.get("state"))
	state = address.get("state").upper().strip()

	# The max length for ISO state codes is 3, excluding the country code
	if len(state) <= 3:
		# PyCountry returns state code as {country_code}-{state-code} (e.g. US-FL)
		address_state = (country_code + "-" + state).upper()

		states = pycountry.subdivisions.get(country_code=country_code.upper())
		states = [pystate.code for pystate in states]

		if address_state in states:
			return state

		frappe.throw(_(error_message))
	else:
		try:
			lookup_state = pycountry.subdivisions.lookup(state)
		except LookupError:
			frappe.throw(_(error_message))
		else:
			return lookup_state.code.split('-')[1]


def sanitize_error_response(response):
	response = response.full_response.get("detail")
	response = response.replace("_", " ")

	sanitized_responses = {
		"to zip": "Zipcode",
		"to city": "City",
		"to state": "State",
		"to country": "Country"
	}

	for k, v in sanitized_responses.items():
		response = response.replace(k, v)

	return response
