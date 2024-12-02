# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'RDP Helpdesk Default User',
    'version': '12.0.1.1',
    'category': 'Helpdesk',
    'author': 'RDP',
    'summary': 'RDP Helpdesk Default User',
    'website': 'www.rdp.in',
    'sequence': '10',

    'depends': ['helpdesk'],
    'data': [
        'views/helpdesk_team_inherit_view.xml',
    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,

}
