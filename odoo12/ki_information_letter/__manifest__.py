# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Information Letter',
    'category': 'Website',
    'website': 'http://www.kiraninfosoft.com',
    'summary': '',
    'version': '1.9',
    'description': "",
    'depends': ['website_mail', 'website_partner', 'website'],
    'data': [
        'data/information_letter_data.xml',
        'views/information_letter_views.xml',
        'views/information_letter_templates.xml',
        'views/snippets.xml',
        'security/ir.model.access.csv',
        'security/information_letter_security.xml',
    ],
    'demo': [
        'data/information_letter_demo.xml'
    ],
    'test': [
    ],
    'qweb': [
    ],
    'application': False,
    'installable': True,
}
