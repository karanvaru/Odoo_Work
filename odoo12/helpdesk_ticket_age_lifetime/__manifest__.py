# -*- coding: utf-8 -*-
{
    'name': "Helpdsek Ticket Age",
    'version': '12.0.1.0.1',
    'license': 'OPL-1' ,
    'summary': """Track helpdesk ticket lifetime in particular stage""",
    'author': "SunArc Technologies",
    'website': "http://www.sunarctechnologies.com",
    'sequence': 1,
    'category': 'Helpdesk',
    # any module necessary for this one to work correctly
    'depends': ['base', 'helpdesk'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/helpdesk_stage_age.xml',
        'data/helpdesk_age_group.xml',
        'report/ticket_age_report.xml',
    ],
    # only loaded in demonstration mode
    'installable': True,
    'auto_install': False,
    'application': True,
}
