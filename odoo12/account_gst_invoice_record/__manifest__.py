# -*- coding: utf-8 -*-
{
    'name': "GST Invoice Records",
    'summary': """Invoice GST Report""",
    'description': """
Invoice GST Report
    """,
    'author': "RDP",
    'website': "www.rdp.in",
    'category': 'Accounting',
    'version': '3.0',
    'depends': [
        'account', 'l10n_in'
    ],
    'data': [
        # 'views/account_invoice_inherite_view.xml',
        'views/account_invoice_report.xml',
    ],
}
