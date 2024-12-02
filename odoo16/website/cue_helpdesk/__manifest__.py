# -*- coding: utf-8 -*-
{
    'name': 'cue Helpdesk',
    'category': 'Helpdesk',
    'version': '1.1.0',
    'summary': 'This App Is Based On Helpdesk',
    'sequence': -100,
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'description': 'cue Helpdesk',
    'depends': [
        'odoo_website_helpdesk'
    ],
    'data': [
        'views/helpdesk_categories_inherit.xml',
        'views/website_form_inherit.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            'cue_helpdesk/static/src/js/search_ticket_type.js',
            'cue_helpdesk/static/src/js/file_validation.js',
        ],
    },

    'application': True,
    'license': 'LGPL-3',
    'demo': [],
}
