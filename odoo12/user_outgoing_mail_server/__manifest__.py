# -*- coding: utf-8 -*-
# Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Outgoing Mail Server Per User',
    'description': 'Set an outgoing mail server for particular user',
    'summary': """ It sends an e-mail from particular user's outgoing
                    mail server
                    """,
    'category': 'Discuss',
    'version': '12.0.1.0.0',
    'author': 'Bizople Solutions Pvt. Ltd.',
    'website': 'https://www.bizople.com/',
    'sequence':1,
    'depends': [
        'base',
        'mail'
    ],
    'data': [
        'views/ir_mail_server_view.xml',
        'views/res_users_view.xml'
    ],

    'images': [
       'static/description/banner.png',
       'static/description/icon.png'
    ],
    'license': 'OPL-1',
    'price': 10,
    'installable': True,
    'application': True,
    'auto_install': False,
    'currency': 'EUR'
}
