# -*- coding: utf-8 -*-
{
    'name': "Time Tracker : RMA Ticket",
    'summary': """Time Tracker : RMA Ticket""",
    'description': """
Time Tracker : RMA Features as below:
- RMA Form

    """,
    'author': "RDP",
    'website': "www.rdp.in",
    'category': 'RMA',
    'version': '1.0',
    'depends': [
        'ki_base_time_tracking',
        'helpdesk','sync_rma'
    ],
    'data': [
        'views/rma_time_tracking_view.xml',
        'views/time_tracking_view.xml',
        'views/action_server_rma.xml',
    ],
}
