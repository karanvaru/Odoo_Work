# -*- coding: utf-8 -*-
# Part of anharaljazeera. See LICENSE file for full copyright and licensing details.
{
    'name': "POS Close Email",
    'summary': "POS Close Email",
    'description': "POS Close Email",
    "version": "1.0",
    'category': 'Sales/Point of Sale',
    'author': "anharaljazeera",
    "depends": [
        'hr',
        'base',
        'point_of_sale',
    ],
    'data': [
        'data/close_session_mail.xml',
        'reports/pos_session_report.xml',
        'views/res_company.xml',
        'views/res_config_settings_inherit_view.xml',
    ],
    "application": False,
    'installable': True,
}
