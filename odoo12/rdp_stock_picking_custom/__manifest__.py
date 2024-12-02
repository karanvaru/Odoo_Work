# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'RDP Stock Picking Custom',
    'version': '12.0.1.0',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'RDP Stock Picking Customizations ',
    'website': 'www.rdp.in',
    'sequence': '10',

    'depends': ['base','stock'],
    'data': [

        'security/ir.model.access.csv',
        'views/stock_picking_custom_view.xml',


    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}
