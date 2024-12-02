# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Disable Quick Create and Edit For Product based on user",
    'summary': "Disable Quick Create and Edit For Product based on user",
    'description': "Disable Quick Create and Edit For Product based on user",
    "version": "1.0",
    "category": "web",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    'price': 10.0,
    'currency': 'EUR',
    'images': ['static/description/image.jpeg'],
    "depends": [
        'web'
    ],
    "data": [
        'security/security.xml',
    ],
    "application": False,
    'installable': True,
    'assets': {
        'web.assets_backend': [
            'ki_disable_quick_create/static/src/js/disable_quick_create.js'
        ]
    }

}
