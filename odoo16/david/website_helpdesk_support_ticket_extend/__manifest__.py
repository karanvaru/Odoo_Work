# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Website Helpdesk Support Ticket Extend",
    'summary': """Website Helpdesk Support Ticket Extend""",
    'description': """Website Helpdesk Support Ticket Extend""",
    "version": "1.0.2",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'OPL-1',
    "depends": [
        'website_helpdesk_support_ticket','website','portal','analytic'
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/portal_user_data.xml',
        'data/mail_data.xml',
        'data/helpdes_team_mail.xml',
        'data/helpdesk_stage_data.xml',
        'data/helpdesk_pending_review_template.xml',
        'wizard/create_task_wizard.xml',
        'views/helpdesk_ticket_extend.xml',
        'views/helpdesk_support_trmplate_inherit.xml',
        'views/helpdesk_support_thanks_page_inherit.xml',
        'views/portal_ticket_menu.xml',
        'views/my_ticket_page_inherit.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_helpdesk_support_ticket_extend/static/src/js/reason_field.js',
        ],
    },
    "application": False,
    'installable': True,
}
