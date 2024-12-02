# -*- coding: utf-8 -*-
{
    'name': "Reddot Report Automate CRM",
    'summary': """Reddot Report Automate CRM""",
    'author': "Reddot Report Automate CRM",
    'category': 'crm',
    'version': '0.2',
    'author': "Reddot Distribution",
    "website": "https://reddotdistribution.com",
    'depends': [
        'base',
        'crm',
        'reddot_report_automate',
    ],
    'data': [
        'data/lead_send_mail_cron.xml',
        'data/lead_close_date_mail_template.xml',
        'data/lead_mail_template.xml',
        'data/report_automation_config_data.xml',
        'views/crm_lead_report_view_inherit.xml',
    ],
}
