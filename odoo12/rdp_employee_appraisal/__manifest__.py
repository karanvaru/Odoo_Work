# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Employee Appraisal',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module help us to Apply Appraisal ',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     Test App
    """,
    'depends': ['base', 'hr'],
    'data': [

        'security/ir.model.access.csv',
        'wizards/application.xml',
        'views/employee_appraisal.xml',
        'data/data.xml',


    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}
