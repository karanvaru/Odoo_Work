# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Search Purchase Order Line on Purchase Order Form",
    'summary': "Search Purchase Order Line on Purchase Order Form",
    'description': "Search Purchase Order Line on Purchase Order Form",
    "version": "1.0",
    "category": "Purchases",
    'price': 15.0,
    'currency': 'EUR',
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    'images': ['static/description/icon.png'],
    "depends": [
        'purchase'
    ],
    "data": [
        # 'views/templates.xml'
        
    ],


    "assets": {
        'web.assets_backend': [
            '/ki_purchase_line_search/static/src/**/*',
        ],
    },
    "application": False,
    'installable': True,
}
