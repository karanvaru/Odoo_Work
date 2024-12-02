# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

{
    'name': "Valuation For Free Of Cost Products",
    'summary': """Valuation For Free Of Cost Products""",
    'description': """Skip Valuation For Free Of Cost Products""",
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
        'views/purchase_order.xml',
        'views/account_move.xml',
        'views/sale_order.xml'
    ],
    "application": False,
    'installable': True,
}
