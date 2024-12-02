# -*- coding: utf-8 -*-
{
    'name': "POS Access To Session Closing Financial Data",
    'summary': "POS Access To Session Closing Financial Data, pos hide closing financial fields, pos hide closing data, pos hide, pos access closing data, pos, access Session Closing data, pos session data access,pos session closing access, pos closing access, pos hide closing data, pos hide closing, pos hide session closing data, pos retail hide closing data, pos hide info pos hide fields pos hide financial data, hide closing pos hide pos closing access pos security pos access closing data pos pos closing session access data pos hide closing data",
    'description': """POS Access To Session Closing Financial Data""",
    'author': "Khaled Hassan",
    'website': "https://apps.odoo.com/apps/modules/browse?search=Khaled+hassan",
    'category': 'Point of Sale',
    'version': '17.0',
    'license': 'OPL-1',
    'currency': 'EUR',
    'price': '25',
    'depends': ['base', 'point_of_sale'],
    "images": ['static/description/main_screenshot.png'],
    'data': [
        'views/views.xml',
        'views/templates.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_hide_closing_fields/static/src/xml/templates.xml',
        ],
    },
}

