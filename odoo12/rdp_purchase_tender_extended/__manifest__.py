# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Purchase Tender Extended',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'Purchase Tendor Extended ',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     
    """,
    'depends': ['base','sh_po_tender_management'],
    'data': [

        'security/ir.model.access.csv',
        'views/purchase_agreement.xml',

    ],

    # 'license': 'OPL-1',
    # 'application': True,
    'installable': True,


}
