# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Part Send Request',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP Workstation Pvt Ltd.',
    'summary': 'This module help us to product send and request details. ',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     To send parts to field engineer
    """,
    'depends': ['base','helpdesk','mail','product','repair'],
    'data': [

        'security/ir.model.access.csv',
        'views/product_details_view.xml',
        'data/data.xml',
    ],

    # 'license': 'OPL-1',
    # 'application': True,
    'installable': True,


}
