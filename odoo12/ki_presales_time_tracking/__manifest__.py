# -*- coding: utf-8 -*-
{
    'name': "Time Tracker : Presales Ticket",
    'summary': """Time Tracker : Presales Ticket""",
    'description': """
Time Tracker : Presales Features as below:
- Presales Form

    """,
    'author': "RDP",
    'website': "www.rdp.in",
    'category': 'Presales',
    'version': '1.0',
    'depends': [
        'ki_base_time_tracking',
        'rdp_presales',
    ],
    'data': [
        'views/presales_time_tracking_view.xml',
        'views/time_tracking_view.xml',
        'views/action_server_presales.xml',
    ],
}
