# -*- coding: utf-8 -*-
{
    'name': "RDP TAT/SLA",
    'version': '12.0.1.0.9',
    'license': 'OPL-1' ,
    'summary': """SLA""",
    'author': "RDP",
    'website': "http://www.rdp.in",
    'sequence': 1,
    'category': 'Helpdesk',
    # any module necessary for this one to work correctly
    'depends': ['base', 'helpdesk', 'rdp_ked_escalation','web'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/helpdesk_ticket.xml',
        # # 'wizard/ticket_sla_stop_wizard_view.xml',
        'data/helpdesk_age_group.xml',
        'data/ticket_status.xml',
        'data/sequence.xml',
        'views/tat_config.xml',
        'views/tat_sla.xml',

        # 'report/ticket_age_report.xml',
    ],
    # only loaded in demonstration mode
    'installable': True,
    'auto_install': False,
    'application': True,
}
