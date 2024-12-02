# -*- coding: utf-8 -*-
{
    'name': "Account Move Line Extended",
    'summary': """product Category in journal item""",
    'description': """
Invoice GST Report
    """,
    'author': "RDP",
    'website': "www.rdp.in",
    'category': 'Accounting',
    'version': '3.0',
    'depends': [
        'account', 'l10n_in','amazon_ept', 'product'
    ],
    'data': [
        # 'views/account_invoice_inherite_view.xml',
        'views/account_move_line_extended.xml',
    ],
}
