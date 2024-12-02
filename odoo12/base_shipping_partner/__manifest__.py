# -*- coding: utf-8 -*-
{
    'name': 'Odoo Shipping Partners',
    'version': '12.0',
    'summary': 'Allows to connect Odoo with multiple shipping providers.',
    'category': 'Warehouse',

    'depends': ['delivery','product'],
    'data':[
            'views/stock_picking_view.xml',
            'views/shipping_partner_view.xml',
            'views/template.xml',
            'views/delivery_carrier_view.xml',
            'security/ir.model.access.csv',
    ],

    'images': ['static/description/base_shipping.png'],

    'author': 'Teqstars',
    'website': 'https://teqstars.com',
    'support': 'support@teqstars.com',
    'maintainer': 'Teqstars',
    "description": """
        - Manage your FedEx operation from Odoo
        - Integration FedEx
        - Connector FedEx
        - FedEx Connector
        - Odoo FedEx Connector
        - FedEx integration
        - FedEx odoo connector
        - FedEx odoo integration
        - FedEx shipping integration
        - FedEx integration with Odoo
        - odoo integration apps
        - odoo FedEx integration
        - odoo integration with FedEx    
        - Manage your UPS operation from Odoo
        - Integration UPS
        - Connector UPS
        - UPS Connector
        - Odoo UPS Connector
        - UPS integration
        - UPS odoo connector
        - UPS odoo integration
        - UPS shipping integration
        - UPS integration with Odoo
        - odoo integration apps
        - odoo UPS integration
        - odoo integration with UPS
        - shipping integration
        - shipping provider integration
        - shipper integration
    """,

    'demo': [],
    'qweb': ['static/src/xml/dashboard.backend.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
    'price': 9.99,
    'currency': 'EUR',
}
