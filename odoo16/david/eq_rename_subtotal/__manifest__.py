# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################

{
    'name' : 'Untaxed Amount to Subtotal',
    'category': 'Sales',
    'version': '16.0.1.0',
    'author': 'Equick ERP',
    'description': """
        Untaxed Amount to Subtotal
    """,
    'summary': 'Untaxed Amount to Subtotal',
    'depends' : ['base', 'sale_management'],
    'price': 00,
    'currency': 'EUR',
    'license': 'OPL-1',
    'website': "",
    'data': [
        'views/sale_order_view.xml',
    ],
    'demo': [],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
