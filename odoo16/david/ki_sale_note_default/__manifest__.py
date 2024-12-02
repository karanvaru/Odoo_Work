# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Ki Sale Note Default",
    'summary': """Ki Sale Note Default""",
    'description': """Ki Sale Note Default""",
    "version": "1.1",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'OPL-1',
    "depends": [
        'sale',
        'sale_management',
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/sale_note_default.xml',
        'views/sale_order_view.xml',
        'report/sale_quotation_order_report.xml',
        # 'views/purchase_order_view.xml',
    ],
    "application": False,
    'installable': True,
}
