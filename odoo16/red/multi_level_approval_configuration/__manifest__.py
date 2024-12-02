# -*- coding: utf-8 -*-
{
    'name': 'Odoo Approval All in One',
    'version': '16.0.1.0',
    'category': 'Approvals',
    'description': """
    Setup the approval flow for all the models: Sale Order, Purchase Order, MRP Order,..
    Centralize all the approval requests in one place which help the manager reviews easily
    """,
    'summary': '''
    Setup the approval flow for all the models: Sale Order, Purchase Order, MRP Order,..
    Centralize all the approval requests in one place which help the manager reviews easily
    ''',
    'live_test_url': 'https://demo15.domiup.com',
    'author': 'Domiup',
    'price': 100,
    'currency': 'USD',
    'license': 'OPL-1',
    'support': 'domiup.contact@gmail.com',
    'website': 'https://apps.domiup.com/slides/odoo-approval-all-in-one-1',
    'depends': [
        'multi_level_approval',
        'advanced_web_domain_widget'
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        'security/security.xml',

        # Wizards
        'wizard/cancel_approval_views.xml',
        'wizard/change_approver_views.xml',

        # Views
        'views/multi_approval_type_views.xml',
        'views/multi_approval_views.xml',

        # Add actions after all views.

        # Add menu after actions.

        # Wizards
        'wizard/request_approval_views.xml',
        'wizard/rework_approval_views.xml',
        'wizard/test_approval_views.xml',
    ],
    'images': ['static/description/banner.gif'],
    'test': [],
    'demo': [],
    'installable': True,
    'active': False,
    'application': True,
}
