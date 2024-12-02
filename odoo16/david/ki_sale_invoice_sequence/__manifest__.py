# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Sale Invoice Sequence",
    'summary': """Sale Invoice Sequence""",
    'description': """Sale Invoice Sequence""",
    "version": "1.6",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'OPL-1',
    "depends": [
        'sale',
        'account',
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/account_journal.xml',
        'views/quote_invoice_sequence.xml',
        'views/sale.xml',
        'views/invoice.xml',
    ],
    "application": False,
    'installable': True,
}
