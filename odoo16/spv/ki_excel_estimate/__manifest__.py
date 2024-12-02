# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

{
    'name': "Ki Excel Estimate",
    'summary': """Excel Estimate""",
    'description': """Excel Estimate""",
    'version': "0.1",
    'category': "Estimate",
    'author': "Kiran Infosoft",
    'website': "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "depends": [
        'sale',
        'base'
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/estimate_excel_view.xml',
        # 'views/pdf_report.xml',
    ],
    'application': False,
    'installable': True,
}
