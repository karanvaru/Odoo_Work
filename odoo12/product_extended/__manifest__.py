# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Products PDF Report',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'Products PDF Report',
    'website': '',
    'sequence': '10',
    'description': """
     Products PDF Report
    """,
    'depends': ['base', 'product'],
    'data': [

        'report/report.xml',
        'report/product_template_report.xml',


    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}
