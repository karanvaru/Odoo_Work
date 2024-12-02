# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Vanilla Four',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module help us to develop basic App ',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     Test App
    """,
    'depends': ['base', 'mail', 'crm'],
    'data': [

        'security/ir.model.access.csv',
        'wizards/application.xml',
        'views/test_app_view.xml',
        'data/data.xml',


    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}
