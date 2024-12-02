# -*- coding: utf-8 -*-
{
    'name': 'Shiprocket Odoo Shipping Connector',
    'version': '13.0',
    'author': "Vraja Technologies",
    'price': 249,
    'currency': 'EUR',
    'category': "Website",
    'summary': "We are providing following modules, shipstation, shipping, odoo shipping integration,odoo shipping connector, dhl express, fedex, ups, gls, usps, stamps.com, shipstation, bigcommerce, easyship, amazon shipping, sendclound, ebay, shopify.",
    'depends': ['delivery','sale_stock','stock_picking_batch'],
    'data': [
        'security/ir.model.access.csv',
        'views/delivery_carrier_view.xml',
        'views/res_company.xml',
        'views/stock_picking.xml',
        'views/batch_orders.xml',
    ],
    'images': [
        'static/description/cover.png',
    ],
 
    'maintainer': 'Vraja Technologies',
    'website': 'www.vrajatechnologies.com',
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',

}