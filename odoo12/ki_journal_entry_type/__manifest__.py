# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

{
    'name': "JE Types in Transactions",
    'summary': """JE Types in Transactions""",
    'description': """JE Types in Transactions""",
    'author': "Kiran Infosoft",
    'website': "www.kiraninfosoft.com",
    'category': 'purchase',
    'version': '3.0',
    'depends': [
        'purchase_stock',
        'account',
        'sale_stock'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_order.xml',
        'views/account_move.xml',
        'views/sale_order.xml',
        'views/stock_picking.xml'
    ],
    "application": False,
    'installable': True,
}
