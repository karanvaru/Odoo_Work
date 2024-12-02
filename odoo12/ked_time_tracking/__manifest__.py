# -*- coding: utf-8 -*-
{
    'name': "Time Tracker : Ked Ticket",
    'summary': """Time Tracker : KED Ticket""",
    'description': """
Time Tracker : KED Features as below:
- KED Form

    """,
    'author': "RDP",
    'website': "www.rdp.in",
    'category': 'KED',
    'version': '1.0',
    'depends': [
        'ki_base_time_tracking',
        'rdp_ked_escalation',
    ],
    'data': [
        'views/ked_time_tracking_view.xml',
        'views/time_tracking_view.xml',
        'views/action_server_ked.xml',
    ],
}
