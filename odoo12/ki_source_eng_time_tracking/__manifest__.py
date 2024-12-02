# -*- coding: utf-8 -*-
{
    'name': "Time Tracker : Source and Engineering Ticket",
    'summary': """Time Tracker : Source and Engineering Ticket""",
    'description': """
Time Tracker : Source and Engineering Features as below:
- Source and Engineering Form

    """,
    'author': "RDP",
    'website': "www.rdp.in",
    'category': 'Source and Engineering',
    'version': '1.0',
    'depends': [
        'ki_base_time_tracking',
        'source_and_eng'

    ],
    'data': [
        'views/source_eng_time_tracking_view.xml',
        'views/time_tracking_view.xml',
        'views/action_server_source_eng.xml',
    ],
}
