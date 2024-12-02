# -*- coding: utf-8 -*-
{
    'name': "Product Management",
    'summary': """Product Management""",
    'description': """Product Management""",
    "license": "OPL-1",
    "author": "RMPS",
    "version": "16.0.1.0.1",
    "depends": [
        'base', 'sale_management', 'stock', 'purchase'
    ],
    "data": [
        'security/ir.model.access.csv',
        'data/cron_view.xml',
        'data/email_template_view.xml',
        'views/product_package_type_view.xml',
        'views/stock_warehouse_inherit_view.xml',
        'views/critical_stock_product_view.xml',
    ],
    "application": False,
    'installable': True,
}
