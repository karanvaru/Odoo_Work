# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Helpdesk Opendays',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module help us to see all open days ',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     
    """,
    'depends': ['base','helpdesk'],
    'data': [

        # 'security/ir.model.access.csv',
        'views/helpdesk_ticket.xml',

    ],

    # 'license': 'OPL-1',
    # 'application': True,
    'installable': True,


}
