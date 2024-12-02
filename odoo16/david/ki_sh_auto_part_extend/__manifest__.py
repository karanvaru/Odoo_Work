# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Sh Auto Part Extend",
    'summary': """Sh Auto Part Extend""",
    'description': """Sh Auto Part Extend""",
    "version": "1.8.0",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "depends": [
        'sh_auto_part_vehicle',
        'product',
    ],
    "data": [
        'security/ir.model.access.csv',
        'data/data_view.xml',
        'wizard/create_product_variant_wizard.xml',
        'views/motorcycle_view.xml',
        'views/product_view.xml',
    ],
    "application": False,
    'installable': True,
}
