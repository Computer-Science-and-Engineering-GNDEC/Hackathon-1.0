# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
from __future__ import unicode_literals

import frappe, json
from frappe.utils.make_random import get_random
from datetime import datetime
from erpnext.demo.setup.setup_data import import_json
import random

def setup_data():
	frappe.flags.mute_emails = True
	make_masters()
	setup_item()
	make_student_applicants()
	make_student_group()
	make_fees_category()
	make_fees_structure()
	make_assessment_groups()
	frappe.db.commit()
	frappe.clear_cache()

def make_masters():
	import_json("Room")
	import_json("Department")
	import_json("Instructor")
	import_json("Course")
	import_json("Program")
	import_json("Student Batch Name")
	import_json("Assessment Criteria")
	import_json("Grading Scale")
	frappe.db.commit()

def setup_item():
	items = json.loads(open(frappe.get_app_path('erpnext', 'demo', 'data', 'item_education.json')).read())
	for i in items:
		item = frappe.new_doc('Item')
		item.update(i)
		item.min_order_qty = random.randint(10, 30)
		item.item_defaults[0].default_warehouse = frappe.get_all('Warehouse',
			filters={'warehouse_name': item.item_defaults[0].default_warehouse}, limit=1)[0].name
		item.insert()

def make_student_applicants():
	blood_group = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
	male_names = []
	female_names = []

	file_path = get_json_path("Random Student Data")
	with open(file_path, "r") as open_file:
		random_student_data = json.loads(open_file.read())
		count = 1

		for d in random_student_data:
			if d.get('gender') == "Male":
				male_names.append(d.get('first_name').title())

			if d.get('gender') == "Female":
				female_names.append(d.get('first_name').title())

		for idx, d in enumerate(random_student_data):
			student_applicant = frappe.new_doc("Student Applicant")
			student_applicant.first_name = d.get('first_name').title()
			student_applicant.last_name = d.get('last_name').title()
			student_applicant.image = d.get('image')
			student_applicant.gender = d.get('gender')
			student_applicant.program = get_random("Program")
			student_applicant.blood_group = random.choice(blood_group)
			year = random.randint(1990, 1998)
			month = random.randint(1, 12)
			day = random.randint(1, 28)
			student_applicant.date_of_birth = datetime(year, month, day)
			student_applicant.mother_name = random.choice(female_names) + " " + d.get('last_name').title()
			student_applicant.father_name = random.choice(male_names) + " " + d.get('last_name').title()
			if student_applicant.gender == "Male":
				student_applicant.middle_name = random.choice(male_names)
			else:
				student_applicant.middle_name = random.choice(female_names)
			student_applicant.student_email_id = d.get('first_name') + "_" + \
				student_applicant.middle_name + "_" + d.get('last_name') + "@example.com"
			if count <5:
				student_applicant.insert()
				frappe.db.commit()
			else:
				student_applicant.submit()
				frappe.db.commit()
			count+=1

def make_student_group():
	for term in frappe.db.get_list("Academic Term"):
		for program in frappe.db.get_list("Program"):
			sg_tool = frappe.new_doc("Student Group Creation Tool")
			sg_tool.academic_year = "2017-18"
			sg_tool.academic_term = term.name
			sg_tool.program = program.name
			for d in sg_tool.get_courses():
				d = frappe._dict(d)
				student_group = frappe.new_doc("Student Group")
				student_group.student_group_name = d.student_group_name
				student_group.group_based_on = d.group_based_on
				student_group.program = program.name
				student_group.course = d.course
				student_group.batch = d.batch
				student_group.academic_term = term.name
				student_group.academic_year = "2017-18"
				student_group.save()
			frappe.db.commit()

def make_fees_category():
	fee_type = ["Tuition Fee", "Hostel Fee", "Logistics Fee",
				"Medical Fee", "Mess Fee", "Security Deposit"]

	fee_desc = {"Tuition Fee" : "Curricular activities which includes books, notebooks and faculty charges" ,
				"Hostel Fee" : "Stay of students in institute premises",
				"Logistics Fee" : "Lodging boarding of the students" ,
				"Medical Fee" : "Medical welfare of the students",
				"Mess Fee" : "Food and beverages for your ward",
				"Security Deposit" : "In case your child is found to have damaged institutes property"
				}

	for i in fee_type:
		fee_category = frappe.new_doc("Fee Category")
		fee_category.category_name = i
		fee_category.description = fee_desc[i]
		fee_category.insert()
		frappe.db.commit()

def make_fees_structure():
	for d in frappe.db.get_list("Program"):
		program = frappe.get_doc("Program", d.name)
		for academic_term in ["2017-18 (Semester 1)", "2017-18 (Semester 2)", "2017-18 (Semester 3)"]:
			fee_structure = frappe.new_doc("Fee Structure")
			fee_structure.program = d.name
			fee_structure.academic_term = random.choice(frappe.db.get_list("Academic Term")).name
			for j in range(1,4):
				temp = {"fees_category": random.choice(frappe.db.get_list("Fee Category")).name , "amount" : random.randint(500,1000)}
				fee_structure.append("components", temp)
			fee_structure.insert()
			program.append("fees", {"academic_term": academic_term, "fee_structure": fee_structure.name, "amount": fee_structure.total_amount})
		program.save()
	frappe.db.commit()

def make_assessment_groups():
	for year in frappe.db.get_list("Academic Year"):
		ag = frappe.new_doc('Assessment Group')
		ag.assessment_group_name = year.name
		ag.parent_assessment_group = "All Assessment Groups"
		ag.is_group = 1
		ag.insert()
		for term in frappe.db.get_list("Academic Term", filters = {"academic_year": year.name}):
			ag1 = frappe.new_doc('Assessment Group')
			ag1.assessment_group_name = term.name
			ag1.parent_assessment_group = ag.name
			ag1.is_group = 1
			ag1.insert()
			for assessment_group in ['Term I', 'Term II']:
				ag2 = frappe.new_doc('Assessment Group')
				ag2.assessment_group_name = ag1.name + " " + assessment_group
				ag2.parent_assessment_group = ag1.name
				ag2.insert()
	frappe.db.commit()


def get_json_path(doctype):
		return frappe.get_app_path('erpnext', 'demo', 'data', frappe.scrub(doctype) + '.json')

def weighted_choice(weights):
	totals = []
	running_total = 0

	for w in weights:
		running_total += w
		totals.append(running_total)

	rnd = random.random() * running_total
	for i, total in enumerate(totals):
		if rnd < total:
			return i
