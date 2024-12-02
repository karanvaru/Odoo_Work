# -*- coding: utf-8 -*-
{
    'name': "Stages History",
    'version': '12.0.1.0.1',
    'license': 'OPL-1' ,
    'summary': """Track Stages History""",
    'author': "RDP",
    'website': "http://www.rdp.in",
    'sequence': 1,
    'category': 'Helpdesk',
    # any module necessary for this one to work correctly
    'depends': ['base', 'helpdesk'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/helpdesk_sla.xml',
        'views/helpdesk_stage_inherit.xml',
        'data/helpdesk_age_group.xml',
        'views/stages_history.xml',
        # 'report/ticket_age_report.xml',
    ],
    # only loaded in demonstration mode
    'installable': True,
    'auto_install': False,
    'application': True,
}
