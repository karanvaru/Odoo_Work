# -*- coding: utf-8 -*-
{
    'name': 'Gati Odoo Shipping Connector',
    'version': '1.0',
    'category': 'Warehouse',
    'summary': 'Integrate & Manage your Gati Shipping Operations from Odoo',

    'depends': ['base_shipping_partner'],

    'data': [
        'data/gati.goods.code.csv',
        'security/ir.model.access.csv',
        'views/shipping_partner_view.xml',
        'views/delivery_carrier_view.xml',
        'views/stock_picking_view.xml',
        'wizard/generate_docket_packet_num_wizard.xml',
        'views/gati_docket_package_number.xml',
        'reports/report_menu.xml',
        'reports/report_gati_label.xml',
    ],

    'images': ['static/description/bluedart_odoo.png'],

    'author': 'Teqstars',
    'website': 'https://teqstars.com',
    'support': 'support@teqstars.com',
    'maintainer': 'Teqstars',
    "description": """
        - Manage your Gati operation from Odoo
        - Integration Gati
        - Connector Gati
        - Gati Connector
        - Odoo Gati Connector
        - Gati integration
        - Gati odoo connector
        - Gati odoo integration
        - Gati shipping integration
        - Gati integration with Odoo
        - odoo integration apps
        - odoo Gati integration
        - odoo integration with Gati
        - shipping integration
        - shipping provider integration
        - shipper integration
        - Gati shipping 
        - Gati delivery
        - USPS, UPS, FedEx, DHL eCommerce, DHL Express, LaserShip, OnTrac, GSO, APC, Aramex, ArrowXL, Asendia, Australia Post, AxlehireV3, BorderGuru, Cainiao, Canada Post
, Canpar, CDL Last Mile Solutions, Chronopost, Colis Privé, Colissimo, Correios, CouriersPlease, Dai Post, Deliv, Deutsche Post, DPD UK, DPD, Blue Dart, Bluedart
        """,

    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
    'price': '800.00',
    'currency': 'EUR',
    # 'live_test_url': 'http://bit.ly/2nuyKPu',
}
