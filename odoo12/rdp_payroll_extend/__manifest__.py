# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'HR Payroll Extend',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    # 'summary': 'This module help us to add SO in HR. ',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     HR Payroll
    """,
    'depends': ['base','l10n_in_hr_payroll'],
    'data': [

        # 'security/ir.model.access.csv',
        'views/hr_payroll_advice_line.xml',
        'data/data.xml',

    ],

    # 'license': 'OPL-1',
    # 'application': True,
    'installable': True,


}
