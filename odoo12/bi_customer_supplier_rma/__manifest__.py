# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Customer and Supplier RMA - Return Merchandise Authorization",
    "version" : "12.0.0.71",
    "category" : "Sales",
    "depends" : ['base','sale','sale_management','purchase','stock','bi_rma','amazon_ept'],
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


    odoo Customer RMA customer Return Orders Management customer Return Merchandise Authorization
    Odoo customer Return Order management for customer
    Odoo customer Return Merchandise Authorization orders customer
    Odoo customer Return Merchandise management orders customer
    Odoo customer Refund order management customer Return order with Odoo customer Product replacement with RMA
    Odoo customer sales replace order customer return order customer refund orders
    Odoo customer RMA Odoo Sales customer RMA Odoo Refund RMA customer Return order RMA
    Odoo website customer RMA website customer Return Merchandise Authorization website customer Return Orders Management
    Odoo customer Return Orders Management for customer Return Orders Management for customer management
    Odoo customer Return Merchandise Authorization customer Return Merchandise Authorization for customer
    odoo customer Return Merchandise Authorization for customer Return Merchandise Authorization for customer
    odoo customer Return Merchandise Authorization customer RMA webshop Return Merchandise management
    odoo customer Return Orders Management customer return order
    odoo customer refund order customer replace order customer return order customer refund order customer replace order


    odoo supplier RMA supplier Return Orders Management supplier Return Merchandise Authorization
    Odoo supplier Return Order management for supplier
    Odoo supplier Return Merchandise Authorization orders supplier
    Odoo supplier Return Merchandise management orders supplier
    Odoo supplier Refund order management supplier Return order with Odoo supplier Product replacement with RMA
    Odoo supplier purchase replace order supplier return order supplier refund orders
    Odoo supplier RMA Odoo Sales supplier RMA Odoo Refund RMA supplier Return order RMA

    odoo purchase RMA purchase Return Orders Management purchase Return Merchandise Authorization
    Odoo purchase order Return Order management for purchase
    Odoo purchase Return Merchandise Authorization orders purchase
    Odoo purchase Return Merchandise management orders supplier
    Odoo purchase Refund order management supplier Return order with Odoo purchase supplier Product replacement with RMA
    Odoo purchase supplier replace order purchase return order purchase refund orders
    Odoo purchase RMA Odoo purchase RMA purchase order RMA Odoo Refund RMA purchase Return order RMA

    Odoo purchase supplier RMA purchase supplier Return Merchandise Authorization purchase supplier Return Orders Management
    Odoo supplier Return Orders Management for supplier Return Orders Management for supplier management
    Odoo supplier Return Merchandise Authorization supplier Return Merchandise Authorization for supplier
    odoo supplier Return Merchandise Authorization for supplier Return Merchandise Authorization for supplier
    odoo supplier Return Merchandise Authorization supplier RMA purchase Return Merchandise management
    odoo supplier Return Orders Management supplier return order
    odoo supplier refund order supplier replace order supplier return order supplier refund order supplier replace order
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
    "price": 60,
    "currency": "EUR",
    "data": [
        'security/ir.model.access.csv',
        'security/rma_security.xml',
        'views/rma_config.xml',
        'views/rma_supplier.xml',
        'views/rma_order_sequence.xml',
        'edi/rma_mail_template.xml',
    ],
    "auto_install": False,
    "installable": True,
    'live_test_url':'https://youtu.be/4zmoKFpHRss',
    "images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
