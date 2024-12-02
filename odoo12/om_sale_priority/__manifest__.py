# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 OM Apps 
#    Email : omapps180@gmail.com
#################################################

{
    'name': 'Sale Priority',
    'category': 'Sales',
    'sequence':5,
    'version': '12.0.1.0',
    'summary': "Plugin will help to Set Quotation Priority,Set Sales Order Priority",
    'description': "Application Set Quotation or sale order priority ",
    'author': 'OM Apps',
    'website': '',
    'depends': ['sale_management'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': True,
    'images' : ['static/description/banner.png'],
    "price": 5,
    "currency": "EUR",
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
