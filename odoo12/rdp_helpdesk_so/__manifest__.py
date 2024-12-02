# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Helpdesk SO Custom',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module help us to add SO in helpdesk. ',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     To send parts to field engineer
    """,
    'depends': ['base','helpdesk','sale'],
    'data': [

        # 'security/ir.model.access.csv',
        'views/so_helpdesk.xml',

    ],

    # 'license': 'OPL-1',
    # 'application': True,
    'installable': True,


}
