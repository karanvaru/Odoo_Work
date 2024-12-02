# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Employee Appraisal inherited',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module help us to Apply Appraisal ',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     Test App
    """,
    'depends': ['base', 'mail','rdp_employee_appraisal'],
    'data': [

        'security/ir.model.access.csv',
        'views/self_appraisal_inherited.xml',
        'data/template.xml',



    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}
