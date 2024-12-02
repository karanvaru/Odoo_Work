# -*- coding: utf-8 -*-
{
    'name': 'Delivery Modifications',
    'version': '1.0',
    'category': 'Stock',
    'summary': 'Delivery/Transfer/Picking modifications',

    'depends': ['delivery'],

    'data': [
        'views/stock_picking_view.xml',
    ],

    'author': 'Teqstars',
    'website': 'https://teqstars.com',
    'support': 'support@teqstars.com',
    'maintainer': 'Teqstars',
    "description": """
        - Added Option to send to shipper before validating incoming shipment.
        - Added Cancel button in order to cancel shipment.
    """,

    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
    'price': '0.00',
    'currency': 'EUR',
}
