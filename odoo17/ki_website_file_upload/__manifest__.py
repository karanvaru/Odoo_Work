# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Upload Documents on Ecommerce Order",
    'summary': """
Upload Documents on Ecommerce Order
""",
    'description': """
Upload Documents on Ecommerce Order
""",
    "version": "1.0",
    "category": "Website",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    'price': 29.0,
    'currency': 'EUR',
    'images': ['static/description/icon.png'],
    "depends": [
        'website_sale',
        'sale'
    ],
    "data": [
        'views/sale_order_form_inherit.xml',
        'views/website_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ki_website_file_upload/static/src/js/web_attachment.js',
        ]
    },
    "application": False,
    'installable': True,
}
