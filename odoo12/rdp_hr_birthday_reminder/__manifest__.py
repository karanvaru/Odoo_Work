
{
    'name': 'RDP Employee Birthday',
    'version': '12.0.0.2',
    'category': 'Human Resources',
    'summary': 'Employee Birthday Wish & Reminder',
    'description': """
        Send email Birthday Wish to Employee
        Send email Reminder To all Employees for Birthday Wish
    """,
    'author': "RDP",
    'depends': ['hr'],
    'data': [
        'data/birthday_reminder_cron.xml',
        'data/mail_templates.xml',
        'data/ir_config_settings_data.xml',
        'views/res_config_settings_views.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
