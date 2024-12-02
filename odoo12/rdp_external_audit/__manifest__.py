# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'External Audit',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'External Audit ',
    'website': 'www.rdp.in',
    'sequence': '12',
    'depends': ['base','mail'],
    'data': [

        'security/ir.model.access.csv',
        'views/external_audit_view.xml',
        'data/data.xml',
       
    ],

    'license': 'OPL-1',
    'application': True,
    'installable': True,


}
