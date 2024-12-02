# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Hower Message",
    'summary': """Hower Message""",
    "version": "17.1",
    'depends': ['account_reports'],
    'data': [
        # 'views/home_page_extend.xml',
    ],
'assets': {
    'web.assets_backend': [
        'hower_message/static/src/**/*',
        # 'account_reports/static/src/js/**/*',
    ],
},
    'installable': True,
    'auto_install': False,
    'application': False,
}
