# -*- coding: utf-8 -*-
{
    'name': "Customer Supplier RMA Extended",
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'Supplier RMA',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     Supplier RMA'
    """,

    # any module necessary for this one to work correctly
    'depends': ['base', 'bi_customer_supplier_rma'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/customer_supplier_extended_view.xml',
    ],
    # 'license': 'OPL-1',
    'application': True,
    'installable': True,

}
