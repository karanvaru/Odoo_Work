# -*- coding: utf-8 -*-
# Part of anharaljazeera. See LICENSE file for full copyright and licensing details.
{
    'name': "Qty Button For Point Of Sale",
    'summary': "Qty Button For Point Of Sale",
    'description': "Qty Button For Point Of Sale",
    "version": "1.0",
    'category': 'Sales/Point of Sale',
    'author': "anharaljazeera",
    "depends": [
        'point_of_sale',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'al_pos_qty_button/static/src/xml/**/*',
            'al_pos_qty_button/static/src/js/**/*',
        ],
    },
    "application": False,
    'installable': True,
}
