# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Cash Request Tickets',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module is used for cash request tickets',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     This module is used for cash request tickets
    """,
    'depends': ['base', 'mail', 'crm','hr_expense','account'],
    'data': [

        'security/ir.model.access.csv',
        # 'wizards/application.xml',
        'views/test_app_view.xml',
        'data/data.xml',


    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}
