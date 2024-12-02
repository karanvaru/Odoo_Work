# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Additional Fees",
    'summary': """Additional Fees""",
    'description': """Additional Fees""",
    "version": "1.5.0",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "depends": [
        'purchase',
        'product',
    ],
    "data": [
        'security/ir.model.access.csv',
        'data/additional_fees_data.xml',
        'views/additional_fees.xml',
        # 'views/purchase_order_line.xml',
        'views/product.xml',
        # 'wizard/purchase_order_line_wizard.xml',
    ],
    "application": False,
    'installable': True,
}
