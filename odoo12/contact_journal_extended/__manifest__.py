# -*- coding: utf-8 -*-
{
    'name': "Contact and Journal Item Pan",
    'summary': """PAN Number""",
    'description': """
To fetch the Pan card number from contact
    """,
    'author': "RDP",
    'website': "www.rdp.in",
    'category': 'contact',
    'version': '3.0',
    'depends': [
        'account', 'contacts', 'stock', 'ki_accounting_reports',
    ],
    'data': [
        'views/contact_journal_extended.xml',
        'views/stock_move_extended.xml'
    ],
}
