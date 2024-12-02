# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Custom Delivery Report',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module help us to generate the pdf reports',
    'website': 'www.rdp.in',
    'sequence': '12',
    'description': """
     To Generate the reports
    """,
    'depends': ['base','stock'],
    'data': [

        'security/ir.model.access.csv',
        'reports/reports.xml',
        'reports/delivary_report.xml',

    ],

    # 'license': 'OPL-1',
    # 'application': True,
    'installable': True,


}
