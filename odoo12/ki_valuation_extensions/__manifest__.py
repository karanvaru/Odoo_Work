# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

{
    'name': "Regenerate Valuation for Missing Transfers",
    'summary': """Regenerate Valuation for Missing Transfers""",
    'description': """Regenerate Valuation for Missing Transfers""",
    'author': "Kiran Infosoft",
    'website': "www.kiraninfosoft.com",
    'category': 'stock',
    'version': '1.6',
    'depends': [
        'stock_account',
        'mrp',
        'sale_margin_customize'
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'data/action_file.xml',
        'wizard/wizard.xml'
    ],
    "application": False,
    'installable': True,
}
