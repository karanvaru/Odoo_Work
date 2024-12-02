# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "RMA - Return Merchandise Authorization/Return Orders Management",
    "version" : "12.0.0.5",
    "category" : "Sales",
    "depends" : ['base','sale','sale_management','stock'],
    "author": "BrowseInfo",
    'summary': 'Manage RMA on Odoo with Return Product, Replace product and  With Refund Order',
    "description": """
    odoo RMA - Return Orders Management/Return Merchandise Authorization
    Odoo Return Order management
    Odoo Return Merchandise Authorization orders
    Odoo Return Merchandise management orders
    Odoo Refund order management Return order with Odoo Product replacement with RMA
    Odoo sales replace order sales return order sales refund orders
    Odoo RMA Odoo Sales RMA Odoo Refund RMA Return order RMA
    Odoo website RMA website Return Merchandise Authorization website Return Orders Management
    Odoo Return Orders Management for website Return Orders Management for shop management
    Odoo Return Merchandise Authorization website Return Merchandise Authorization for website
    odoo Return Merchandise Authorization for shop Return Merchandise Authorization for webshop
    odoo webshop Return Merchandise Authorization webshop RMA webshop Return Merchandise management
    odoo webshop Return Orders Management website return order
    odoo website refund order website replace order webshop return order webshop refund order webshop replace order


This Module allow the seller to recharge wallet for the customer. 
    website return order
    website RMA webstore
    webshop RMA webshop
    webstore Return material authorization webstore
    webshop return goods management on webshop

    eCommerce RMA eCommerce
    eCommerce return order
    webshop RMA website
    webshop return order
    website Return Orders Management on website
    website Return Merchandise Authorization on website
    webshop Return Orders Management on website
    webshop Return Merchandise Authorization
    eCommerce Return Orders Management
    eCommerce Return Merchandise Authorization
    website return order from website
    webshop retrun order from webshop
    webstore return order from webstore
    """,
    "website" : "https://www.browseinfo.in",
    "price": 69,
    "currency": "EUR",
    "data": [
        'security/ir.model.access.csv',
        'views/rma_view.xml',
        'views/rma_config.xml',
        'views/rma_order_sequence.xml',
        'edi/rma_mail_template.xml',
    ],
    "auto_install": False,
    "installable": True,
    'live_test_url':'https://youtu.be/rD8KhwqwpZQ',
    "images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
