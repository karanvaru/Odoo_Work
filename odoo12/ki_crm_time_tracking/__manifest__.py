# -*- coding: utf-8 -*-
{
    'name': "Time Tracker : CRM",
    'summary': """Time Tracker : CRM""",
    'description': """
Time Tracker : CRM Featuers as below:
- Lead Form

    """,
    'author': "Kiran Infosoft",
    'website': "www.kiraninfosoft.com",
    'category': 'CRM',
    'version': '1.5',
    'depends': [
        'ki_base_time_tracking',
        'crm'
    ],
    'data': [
        'views/crm_time_tracking_view.xml',
        'views/time_tracking_view.xml',
        'views/action_server_crm.xml',
    ],
}
