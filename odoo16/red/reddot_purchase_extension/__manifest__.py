# -*- coding: utf-8 -*-
{
    'name': "Reddot Purchase Extension",
    'summary': """Reddot Purchase Extension""",
    'author': "Reddot Purchase Extension",
    'category': 'Uncategorized',
    'version': '0.8',
    "website": "https://reddotdistribution.com",
    'depends': [
        'purchase',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_order.xml',
        'reports/purchase_report.xml',
    ],
}
