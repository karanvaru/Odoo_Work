# -*- coding: utf-8 -*-
# Part of anharaljazeera. See LICENSE file for full copyright and licensing details.
{
    'name': "Line Delete Point Of Sale",
    'summary': "Line Delete Point Of Sale",
    'description': "Line Delete Point Of Sale",
    "version": "1.0",
    'category': 'Sales/Point of Sale',
    'author': "anharaljazeera",
    "depends": [
        'point_of_sale'
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'al_pos_line_delete/static/src/xml/**/*',
            'al_pos_line_delete/static/src/js/**/*',
        ],
    },
    "application": False,
    'installable': True,
}
