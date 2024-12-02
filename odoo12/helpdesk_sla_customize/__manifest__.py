# -*- coding: utf-8 -*-
{
    'name': 'Helpdesk SLA Customize',
    'version': '1.0.0.0',
    'category': 'Helpdesk',
    'sequence': 57,
    'summary': 'Track help tickets',
    'website': 'www.sunarctechnologies.com',
    'depends': [
        'helpdesk',
        'base_setup',
        'mail',
        'utm',
        'rating',
        'web_tour',
        'resource',
        'portal',
        'digest',
    ],
    'description': """
        This module mainly use for the added new feature in odoo12 helpdesk same as odoo 13 HelpDesk Module.
    """,
    'data': [
        'security/ir.model.access.csv',
        'views/helpdesk_ticket.xml',
    ],
    'application': True,
}
