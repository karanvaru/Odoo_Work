# -*- coding: utf-8 -*-
{
    'name': 'Blue Dart Odoo Shipping Connector',
    'version': '1.0',
    'category': 'Warehouse',
    'summary': 'Integrate & Manage your Blue Dart Shipping Operations from Odoo',

    'depends': ['base_shipping_partner'],

    'data': [
        'data/bluedart_service.xml',
        'security/ir.model.access.csv',
        'views/shipping_partner_view.xml',
        'views/delivery_carrier_view.xml',
        'views/stock_picking_view.xml',
    ],

    'images': ['static/description/bluedart_odoo.png'],

    'author': 'Teqstars',
    'website': 'https://teqstars.com',
    'support': 'support@teqstars.com',
    'maintainer': 'Teqstars',
    "description": """
        - Manage your Blue Dart operation from Odoo
        - Integration Blue Dart
        - Connector Blue Dart
        - Blue Dart Connector
        - Odoo Blue Dart Connector
        - Blue Dart integration
        - Blue Dart odoo connector
        - Blue Dart odoo integration
        - Blue Dart shipping integration
        - Blue Dart integration with Odoo
        - odoo integration apps
        - odoo Blue Dart integration
        - odoo integration with Blue Dart
        - shipping integration
        - shipping provider integration
        - shipper integration
        - Blue Dart shipping 
        - Blue Dart delivery
        - USPS, UPS, FedEx, DHL eCommerce, DHL Express, LaserShip, OnTrac, GSO, APC, Aramex, ArrowXL, Asendia, Australia Post, AxlehireV3, BorderGuru, Cainiao, Canada Post
, Canpar, CDL Last Mile Solutions, Chronopost, Colis Privé, Colissimo, Correios, CouriersPlease, Dai Post, Deliv, Deutsche Post, DPD UK, DPD, Blue Dart, Bluedart
        """,

    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
    'price': '90.00',
    'currency': 'EUR',
    # 'live_test_url': 'http://bit.ly/2nuyKPu',
}
