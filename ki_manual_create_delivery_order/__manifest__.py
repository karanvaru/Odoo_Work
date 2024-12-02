# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Manual Delivery Order",
    'summary': """Manual Delivery Order""",
    'description': """Manual Delivery Order""",
    "version": "1.16.0",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "depends": [
        'base',
        'sale_management',
        'stock',
        'sale_stock'
    ],
    "data": [
        'security/ir.model.access.csv',
        'wizard/add_sale_order_line_wizard_view.xml',
        'views/stock_picking_inherit_view.xml',
        # 'views/sale_order_view_inherit.xml',
    ],
    "application": False,
    'installable': True,
}
