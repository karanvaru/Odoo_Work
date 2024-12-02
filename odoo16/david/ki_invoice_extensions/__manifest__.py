# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Invoice Extensions",
    'summary': """Invoice Extensions""",
    'description': """Invoice Extensions""",
    "version": "1.3.2",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "depends": [
        'account'
        # 'sale',
        # 'ki_job_card_extend',
    ],
    "data": [
        'report/report_invoice.xml',
        'report/account_move_inherit_report.xml',
        'views/account_move_view.xml'
    ],
    "application": False,
    'installable': True,
}
