# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

{
    'name': "Sale and Invoice Lot",
    'summary': """Sale and Invoice Lot""",
    'description': """Sale and Invoice Lot""",
    'version': "0.2",
    'category': "CRM",
    'author': "Kiran Infosoft",
    'website': "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "depends": [
        'crm', 'sale','sale_stock'
    ],
    "data": [
        'views/account_move_view.xml',
        'views/report_invoice.xml'
    ],
    'application': False,
    'installable': True,
}
