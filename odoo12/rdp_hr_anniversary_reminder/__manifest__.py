# -*- coding: utf-8 -*-
{
    'name': 'Anniversary Wish & Reminder',
    'version': '12.0.0.1',
    'category': 'Human Resources',
    'summary': 'Employee Anniversary Wish & Reminder',
    'description': """
        Send email Anniversary Wish to Employee
        
    """,
    'author': "RDP",
    'website': "https://heliconia.io/",
    'depends': ['hr'],
    'data': [
        'data/anniversary_reminder_cron.xml',
        'data/mail_templates.xml',
        'data/ir_config_settings_data.xml',
        'views/res_config_settings_views.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
