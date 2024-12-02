# -*- coding: utf-8 -*-
{
    'name': "Invoice Tax Report",
    'summary': """Invoice Tax Report""",
    'description': """
Invoice Tax Report
    """,
    'author': "Kiran Infosoft",
    'website': "www.kiraninfosoft.com",
    'category': 'Accounting',
    'version': '3.1',
    'depends': [
        'account', 'l10n_in','account_gst_invoice_record','account_gst_invoice_record'
    ],
    'data': [
        'views/account_invoice_inherite_view.xml',
    ],
}
