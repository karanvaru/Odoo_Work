# -*- coding: utf-8 -*-
{
    'name': "Time Tracker : RDP DX",
    'summary': """Time Tracker : RDP DX""",
    'description': """
Time Tracker : Marketing App Features as below:
- RDP DX 

    """,
    'author': "RDP",
    'website': "www.rdp.in",
    'category': 'DX',
    'version': '1.0',
    'depends': [
        'ki_base_time_tracking',
        'rdp_dx_page',
    ],
    'data': [
        'views/dx_time_tracking_view.xml',
        'views/time_tracking_view.xml',
        'views/action_server_dx.xml',
    ],
}
