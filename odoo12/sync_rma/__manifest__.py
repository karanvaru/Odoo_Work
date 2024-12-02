# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'RMA with Replace, Repair & Refund',
    'version': '1.0.1',
    'category': 'Project',
    'author': 'Synconics Technologies Pvt. Ltd.',
    'summary': 'Allows to create RMA for the replace, repair products or refund invoice',
    'website': 'www.synconics.com',
    'description': """
RMA with Replace, Repair & Refund
=================================
* This application allows to create RMA the replace, repair products or refund invoice.

    """,
    'depends': ['sale_management', 'sale_stock', 'repair', 'account_check_printing', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/ir_sequence_data.xml',
        'report/report.xml',
        'report/report_rma.xml',
        'data/mail_template.xml',
        'wizard/account_invoice_refund_view.xml',
        'views/res_config_view.xml',
        'views/res_partner_view.xml',
        'views/stock_picking_views.xml',
        'wizard/rma_reject_wiz_view.xml',
        'wizard/generate_rma_lines_view.xml',
        'views/rma_issue_view.xml',
        'views/sale_view.xml',
        'views/account_invoice_view.xml',
        'views/repair_views.xml',
        'menu.xml'
    ],
    'demo': [
        'demo/rma_product_demo.xml',
        'demo/sale_order_demo.xml',
        'demo/rma_demo.xml',
    ],
    'images': ['static/description/main_screen.jpg'],
    'price': 100.0,
    'currency': 'EUR',
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
}
