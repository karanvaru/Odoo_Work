# -*- coding: utf-8 -*-
{
    'name': "Sales Shop Account",
    'summary': """Sales Shop Account""",
    'description': """Sales Shop Account""",
    "license": "OPL-1",
    "author": "RMPS",
    "version": "16.0.1.0.1",
    "depends": [
        'sale',
        'mtrmp_sales_shop',
        'invoice_from_picking',
        'account_payment_multi_deduction',
        'accounting_pdf_reports'
    ],
    "data": [
        'security/ir.model.access.csv',
        'data/link_with_payment_in_flipcart.xml',
        'wizard/trial_balance.xml',
        'views/account_group_view.xml',
        'views/sale_shop_inherit_view.xml',
        'views/stock_picking_inherit_view.xml',
        'report/report_trial_balance.xml'
    ],
    "application": False,
    'installable': True,
}
