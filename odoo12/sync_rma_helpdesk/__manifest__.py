# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Helpdesk RMA with Replace, Repair & Refund',
    'version': '1.0',
    'category': 'Project',
    'author': 'Synconics Technologies Pvt. Ltd.',
    'summary': 'Allows to create RMA for the replace, repair products or refund invoice',
    'website': 'www.synconics.com',
    'description': """
RMA with Replace, Repair & Refund
=================================
* This application allows to create RMA the replace, repair products or refund invoice.

    """,
    'depends': ['sync_rma', 'helpdesk'],
    'data': [
        'views/stock_picking_views.xml',
        'views/helpdesk_ticket_view.xml',
        'views/rma_issue_view.xml',
        'views/account_invoice_view.xml',
    ],
    'demo': [],
    'images': ['static/description/main_screen.jpg'],
    'price': 0.0,
    'currency': 'EUR',
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
}
