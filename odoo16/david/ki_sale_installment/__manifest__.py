# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Sale Installment",
    'summary': "Sale Installment",
    'description': "Sale Installment",
    "version": "1.1",
    "category": "Sales",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "depends": [
        'account',
        'sale',
        'ki_sale_invoice_sequence',
        'om_account_asset'
        # 'base_accounting_kit'
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/sale_order_inherit_view.xml',
        'views/account_asset_asset_inherit_view.xml',
        'views/account_move_inheirt_view.xml',
        'views/sale_installment_plan_view.xml'
    ],
    "application": False,
    'installable': True,
}
