# -*- coding: utf-8 -*-
# Part of anharaljazeera. See LICENSE file for full copyright and licensing details.
{
    'name': "Pending Sales For Point Of Sale",
    'summary': "Pending Sales For Point Of Sale",
    'description': "Pending Sales For Point Of Sale",
    "version": "1.0",
    'category': 'Sales/Point of Sale',
    'author': "anharaljazeera",
    "depends": [
        'point_of_sale',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'al_pos_pending_sales/static/src/xml/**/*',
            'al_pos_pending_sales/static/src/js/**/*',
        ],
    },
    "application": False,
    'installable': True,
}
