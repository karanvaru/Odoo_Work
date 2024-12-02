# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Marketing App',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module help us to develop marketing App ',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     Marketing App
    """,
    'depends': ['base', 'mail', 'crm'],
    'data': [

        'security/ir.model.access.csv',
        'security/security.xml',
        'wizards/application.xml',
        'views/marketing_app.xml',
        'data/data.xml',
        'data/created_status_template.xml',
        'data/closing_update_mail.xml'


    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}
