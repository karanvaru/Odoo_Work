# -*- coding: utf-8 -*-
# Part of anharaljazeera. See LICENSE file for full copyright and licensing details.
{
    'name': "Pos Amounts",
    'summary': "Pos Amounts",
    'description': "Pos Amounts",
    "version": "1.0",
    'category': 'Sales/Point of Sale',
    'author': "anharaljazeera",
    "depends": [
        'point_of_sale',
    ],
    'data': [
        'views/pos_session_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'al_pos_amounts/static/src/xml/**/*',
            'al_pos_amounts/static/src/js/**/*',
        ],
    },
    "application": False,
    'installable': True,
}
