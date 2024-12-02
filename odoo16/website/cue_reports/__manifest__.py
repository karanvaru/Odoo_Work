# -*- coding: utf-8 -*-
{
    'name': 'Cue Reports',
    'category': 'Reports',
    'version': '1.1.0',
    'summary': 'This App Is Based On Reports',
    'sequence': -100,
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'description': 'Cue Reports',
    'depends': ['base', 'account', 'sale', 'purchase','web'],
    'data': [
        'report/cue_report.xml',
        'report/account_move_report.xml',
        'report/purchase_order_report.xml',
        'report/sale_order_report.xml',
        'report/delivery_order_report.xml',
        'views/account_move_inherit.xml',
        'views/purchase_order_inherit.xml',
        'views/sale_order_inherit.xml',

    ],


    'application': True,
    'license': 'LGPL-3',
    'demo': [],
}
