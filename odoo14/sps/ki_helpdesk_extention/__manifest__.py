# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Helpdesk Extention",
    'summary': """""",
    'description': "",
    "version": "14.0",
    "category": "Helpdesk",
    'author': "Kiran Infosoft",
    "website": "https://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "depends": [
        'helpdesk_mgmt',
        'l10n_in',
        'website',
    ],
    "data": [
        "data/helpdesk_data.xml",
        'security/ir.model.access.csv',
        'wizard/assign_user_ticket_view.xml',
        'wizard/mark_done_wizard_view.xml',
        'views/helpdesk_view.xml',
        'views/helpdesk_template.xml',
        'views/helpdesk_category_view.xml',
    ],
    'installable': True,
}
