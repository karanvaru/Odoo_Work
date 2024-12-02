# -*- coding: utf-8 -*-
{
    'name': 'Hr Payroll Extension',
    'category': 'Payroll',
    'version': '1.1.0',
    'summary': 'this app is based on Payroll',
    'sequence': -100,
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'description': 'Hr Payroll Extension',
    'depends': [
        'hr_payroll_community'
    ],
    'images': ['static/description/logo.png'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/payslip_done_wizard_view.xml',
        'views/hr_payslip_inherit.xml',
#         'data/salary_data.xml',
    ],
    'application': True,
    'license': 'LGPL-3',
    'demo': [],
}
