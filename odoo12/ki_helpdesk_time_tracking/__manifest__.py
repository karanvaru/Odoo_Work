# -*- coding: utf-8 -*-
{
    'name': "Time Tracker : Helpdesk Ticket",
    'summary': """Time Tracker : Helpdesk Ticket""",
    'description': """
Time Tracker : Helpdesk Features as below:
- Helpdesk Form

    """,
    'author': "RDP",
    'website': "www.rdp.in",
    'category': 'Helpdesk',
    'version': '1.0',
    'depends': [
        'ki_base_time_tracking',
        'helpdesk'
    ],
    'data': [
        'views/helpdesk_time_tracking_view.xml',
        'views/time_tracking_view.xml',
        'views/action_server_helpdesk.xml',
    ],
}
