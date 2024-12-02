# -*- coding: utf-8 -*-
{
    'name': "Order Delivery Manual",
    'summary': """Order Delivery Manual""",
    'description': """Order Delivery Manual""",
    "license": "OPL-1",
    "author": "RMPS",
    "version": "15.19.07.22",
    "depends": [
        'base', 'sale_management', 'stock', 'delivery'
    ],
    "data": [
        'data/action_file.xml',
        #'views/stock_picking_inherit.xml',
        #'views/res_config_setting.xml',
    ],
    "application": False,
    'installable': True,
}
