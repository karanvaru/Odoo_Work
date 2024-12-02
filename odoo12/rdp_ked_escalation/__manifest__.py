# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'KAM Escalation 1.1',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module help us to add features in heldesk team ',
    'website': 'www.rdp.in',
    'sequence': '10',
    'depends': ['base','helpdesk','mail','rdp_global_feedback'],
    'data': [

        'security/ir.model.access.csv',
        'security/security.xml',
        # 'wizards/quality_check.xml',
        'views/ked_escalation_view.xml',
        'views/helpdesk_ticket_view.xml',
        'views/global_feedback.xml',
        'data/data.xml',
        'data/ticket_create_mail.xml',
        'data/ticket_close_mail.xml',
        'data/warning_template.xml',


    ],

    'license': 'OPL-1',
    'application': True,
    'installable': True,


}
