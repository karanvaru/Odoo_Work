# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Helpdesk Inward Extend',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module help us to calculate inward opendays ',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     To send parts to field engineer
    """,
    'depends': ['base','helpdesk','stock','sync_rma'],
    'data': [

        # 'security/ir.model.access.csv',
        'views/helpdesk_inward_date.xml',

    ],

    # 'license': 'OPL-1',
    # 'application': True,
    'installable': True,


}
