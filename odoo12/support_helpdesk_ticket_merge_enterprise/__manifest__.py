# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
#See LICENSE file for full copyright and licensing details.

{
    'name': 'Merge Helpdesk Support Tickets and Issues Enterprise',
    'depends': [
        'helpdesk'
    ],
    'currency': 'EUR',
    'price': 108.0,
    'license': 'Other proprietary',
    'summary': """This module allow you to merge tickets of your helpdesk support system in Odoo Enterprise.""",
    'description': """
helpdesk support ticket
tickets merge
merge tickets
merge ticket
merge support ticket
merge helpdesk support tickets

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'images': ['static/description/img.png'],
    ##'live_test_url': 'https://youtu.be/m1FjfRpWzrA',
    #'live_test_url': 'https://youtu.be/GGGnD9UFVWg',
    'support': 'contact@probuse.com',
    'version': '1.6',
    'category': 'Project',
    'data': [
        'wizard/merge_ticket_wizard.xml',
        'views/helpdesk_ticket_view.xml',
        'data/closing_mail.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
