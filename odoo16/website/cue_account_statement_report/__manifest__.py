# -*- coding: utf-8 -*-
{
    'name': 'Cue Account Statement Report',
    'category': 'Account',
    'version': '1.1.0',
    'summary': 'This App Is Based On Account',
    'sequence': -100,
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'description': 'Cue Account',
    'depends': [
        'base',
        'account',
        'dynamic_accounts_report',
        'hr_expense',
        'product'
    ],
    'data': [
        'security/ir.model.access.csv',
        # 'wizard/fund_statement_wizard.py',
        'views/capex_category_view.xml',
        'views/fund_statement_view.xml',
        'views/account_account_view.xml',
        'views/product_product_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'cue_account_statement_report/static/src/js/fund_statement.js',
            'cue_account_statement_report/static/src/xml/fund_statement_template.xml',
        ],
    },

    'application': True,
    'license': 'LGPL-3',
    'demo': [],
}
