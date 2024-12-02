# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

{
    'name': "GST Taxes based on HSN Configuration",

    'summary': """
GST Taxes from hsn configuration
""",

    'description': """
GST Taxes from hsn configuration
    """,
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'category': 'Accounting',
    'version': '1.5',
    'depends': ['base','account','sale','purchase','l10n_in'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',

        'views/account_hsn_taxes_views.xml',
#         'views/purchase_order_from_inherit.xml',
        'views/account_move_form_inherit.xml',
#         'views/sale_order_form_inherit.xml',
        'views/product_from_view_inherit.xml',
        'views/state_view.xml',

        'reports/gst_invoice_reg.xml',
        'reports/gst_tax_invoice_view.xml',
        # 'reports/gst_purchase_reg.xml',
        # 'reports/gst_purchase_order_view.xml',
        # 'reports/gst_sale_reg.xml',
        # 'reports/gst_sale_order_view.xml',
    ],
}
