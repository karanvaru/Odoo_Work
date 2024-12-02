# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

{
    'name': "Helpdesk Ticket Extends",
    'summary': """Helpdesk Ticket Extends""",
    'description': """Helpdesk Ticket Extends""",
    'version': "0.20",
    'category': "CRM",
    'author': "Kiran Infosoft",
    'website': "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "depends": [
        'website_helpdesk_form', 'helpdesk', 'website_form'
    ],
    "data": [
        'security/security.xml',
        'views/helpdesk_ticket_view.xml',
        'views/res_users_view.xml',
        'views/portal_template.xml',
        'views/assets.xml'
    ],
    'application': False,
    'installable': True,
}
