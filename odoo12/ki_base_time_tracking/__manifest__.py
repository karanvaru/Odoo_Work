# -*- coding: utf-8 -*-

{
    'name': "RDP Time Sheets",
    'summary': """RDP Time Sheets""",
    'description': """
        Base Module for RDP Time Sheets
    """,
    'author': "Kiran Infosoft",
    'website': "www.kiraninfosoft.com",
    'category': 'Extra Tools',
    'version': '1.6',
    'depends': ['base', 'web_grid'],
    'data': [
        'security/ir.model.access.csv',
        'views/asset_templates.xml',
        'views/time_tracking_view.xml',
        'wizard/time_tracking_wizard_view.xml',
    ],
}
