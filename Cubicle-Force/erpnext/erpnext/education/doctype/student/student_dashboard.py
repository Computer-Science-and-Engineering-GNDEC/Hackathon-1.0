from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'heatmap': True,
		'heatmap_message': _('This is based on the attendance of this Student'),
		'fieldname': 'student',
		'non_standard_fieldnames': {
			'Bank Account': 'party'
		},
		'transactions': [
			{
				'label': _('Admission'),
				'items': ['Program Enrollment', 'Course Enrollment']
			},
			{
				'label': _('Student Activity'),
				'items': ['Student Log', 'Student Group', ]
			},
			{
				'label': _('Assessment'),
				'items': ['Assessment Result']
			},
			{
				'label': _('Student LMS Activity'),
				'items': ['Course Activity', 'Quiz Activity' ]
			},
			{
				'label': _('Attendance'),
				'items': ['Student Attendance', 'Student Leave Application']
			},
			{
				'label': _('Fee'),
				'items': ['Fees', 'Bank Account']
			}
		]
	}
