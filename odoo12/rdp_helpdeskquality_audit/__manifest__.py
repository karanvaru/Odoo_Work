# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Quality Audit',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module help us to add features in heldesk team ',
    'website': 'www.rdp.in',
    'sequence': '10',
    'depends': ['base','helpdesk','mail','rdp_ked_escalation'],
    'data': [

        'security/ir.model.access.csv',
        
        'views/quality_audit_view.xml',
        'views/helpdesk_ticket_view.xml',
        'data/data.xml',
        'data/ticket_create_mail.xml',
        # 'data/server_action.xml',
        'data/ticket_close_mail.xml',
        'data/ticket_closing_remainder.xml',
        'wizards/qa_check.xml',
    ],

    'license': 'OPL-1',
    'application': True,
    'installable': True,


}
