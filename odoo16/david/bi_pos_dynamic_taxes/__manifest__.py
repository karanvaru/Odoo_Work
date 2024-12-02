# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': "POS Taxes | POS Dynamic Taxes | POS Order Line Tax Selection",
    'version': '16.0.0.3',
    'category': 'Point of Sale',
    'summary': 'Point of Sale order line tax selection point of sale tax pos order line taxes on pos multi taxes pos multiple taxes pos multi tax selection pos order multi taxes selection on point of sales multi taxes point of sale dynamic taxes pos order line dynamic tax',
    'description': """ The POS Dynamic Tax is a powerful odoo app designed to enhance the tax management capabilities of the Point of Sale (POS) system in Odoo. This app enables businesses to dynamically apply and manage multiple taxes on products, ensuring accurate and flexible tax calculations at the point of sale. """,
    'author': 'BrowseInfo',
    'website': "https://www.browseinfo.com/demo-request?app=bi_pos_dynamic_taxes&version=16&edition=Community",
    'price': 35,
    'currency': 'EUR',
    'depends': ['base', 'point_of_sale', 'pos_restaurant'],
    'data': [
        'views/pos_config.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'bi_pos_dynamic_taxes/static/src/css/pos.css',
            'bi_pos_dynamic_taxes/static/src/js/models.js',
            'bi_pos_dynamic_taxes/static/src/js/Popups/TaxesTypePopup.js',
            'bi_pos_dynamic_taxes/static/src/js/Screens/ProductScreen/ControlButtons/AddTaxesButton.js',
            'bi_pos_dynamic_taxes/static/src/js/Screens/ProductScreen/ProductScreen.js',
            'bi_pos_dynamic_taxes/static/src/xml/Popups/TaxesTypePopup.xml',
            'bi_pos_dynamic_taxes/static/src/xml/Screens/ProductScreen/ControlButtons/AddTaxesButton.xml',
            'bi_pos_dynamic_taxes/static/src/xml/Screens/ProductScreen/Orderline.xml',
            'bi_pos_dynamic_taxes/static/src/xml/Screens/ProductScreen/OrderSummary.xml',
        ],
    },
    'license': 'OPL-1',
    'installable': True,
    'application': False,
    'auto_install': False,
    'live_test_url':'https://www.browseinfo.com/demo-request?app=bi_pos_dynamic_taxes&version=16&edition=Community',
    "images":["static/description/Banner.gif"],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
