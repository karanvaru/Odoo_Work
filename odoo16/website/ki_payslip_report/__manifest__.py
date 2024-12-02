# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Payslip Report",
    'summary': """Payslip Report""",
    'description': """Payslip Report""",
    "version": "1.3.0",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "depends": [
        'hr_payroll_community'
    ],
    "data": [
        'report/payslip_report_paperformat.xml',
        'report/payslip_report.xml',
    ],
    "application": False,
    'installable': True,
}
