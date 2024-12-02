# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Sale Extensions",
    'summary': """Sale Extensions""",
    'description': """Sale Extensions""",
    "version": "1.3.0",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "depends": [
        'sale',
        'sh_auto_part_vehicle',
    ],
    "data": [
        'security/ir.model.access.csv',
        'wizard/product_view_specification_wizard.xml',
        'views/sale_line_extend.xml',
        'report/quotation_extend.xml',
    ],
    "application": False,
    'installable': True,
}
