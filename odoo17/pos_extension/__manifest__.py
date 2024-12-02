# -*- coding: utf-8 -*-
# Part of anharaljazeera. See LICENSE file for full copyright and licensing details.
{
    'name': "Extension for point of sale",
    'summary': "Extension for point of sale",
    'description': "Extension for point of sale",
    "version": "1.0",
    'category': 'Sales/Point of Sale',
    'author': "anharaljazeera",
    "website": "",
    "depends": [
        'point_of_sale',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_extension/static/src/xml/**/*',
        ],
    },
    "application": False,
    'installable': True,
}
