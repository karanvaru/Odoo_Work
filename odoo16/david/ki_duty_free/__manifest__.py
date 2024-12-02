# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Duty Free Reports",
    'summary': """Duty Free Reports""",
    'description': """Duty Free Reports""",
    "version": "1.5.0",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "depends": [
        'sale',
    ],
    "data": [
        'reports/account_duty_free_report.xml',
        'reports/duty_free_report.xml',
        'views/sale_order_view.xml',
        'views/account_move_view.xml',
    ],
    "application": False,
    'installable': True,
}
