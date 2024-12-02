# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

{
    'name': "Export Import Access",
    'summary': """Export Import Access""",
    'description': """
Module allow to restriction on Export Import options
========================================================
Export Import
Export
Import
Access
Restriction
    """,
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'category': 'Extra Tools',
    'version': '1.0',
    'license': 'Other proprietary',
    'price': 17.0,
    'currency': 'EUR',
    'images': ['static/description/logo.png'],
    'depends': [
        'web','base_import'
    ],
    'data': [
        'security/security.xml',
        'views/templates.xml',
    ],
    'qweb': [
        "ki_export_import_access/static/src/xml/base.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'ki_export_import_access/static/src/js/widget.js'
        ],
    },

}