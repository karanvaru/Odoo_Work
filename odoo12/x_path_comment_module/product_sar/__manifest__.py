# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Part Send Pickup Request',
    'version': '12.1.0.2',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module help us to product Send and Pickup Request details. ',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     To send parts to field engineer
    """,
    'depends': ['base','helpdesk','mail','product','repair','rdp_ked_escalation','bi_customer_supplier_rma'],
    'data': [

        'security/ir.model.access.csv',
        'security/security.xml',
        'wizards/action_to_purchase_request_view.xml',
        'views/product_details_view.xml',
        'data/data.xml',
    ],

    # 'license': 'OPL-1',
    # 'application': True,
    'installable': True,


}
