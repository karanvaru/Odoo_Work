# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Attendance/Leave Analysis Summary",
    'summary': 'Attendance/Leave Analysis Summary'
    'Attendance Report'
    'Leave Report'
    'Calendar',
    'description': """
Attendance/Leave Analysis Summary
Attendance Report
Leave Report
Calendar
""",
    "version": "1.0",
    "category": "Human Resources",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    'price': 49.0,
    'currency': 'EUR',
    'images': ['static/description/icon.jpeg'],
    "depends": [
        'hr_attendance',
        'hr_holidays'
    ],
    "data": [
        'security/ir.model.access.csv',
        'wizard/attendance_summary_report.xml',
    ],
    "application": False,
    'installable': True,
}
