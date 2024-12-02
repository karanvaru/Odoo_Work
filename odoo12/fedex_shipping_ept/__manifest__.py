# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    # App information

    'name': 'Fedex Odoo Shipping Connector',
    'version': '12.0',
    'category': 'Website',
    'summary': 'Odoo FedEx Shipping Integration helps you connect Odoo with FedEx and manage your Shipping operations directly from Odoo.',
    'license': 'OPL-1',

    # Dependencies

    'depends': ['shipping_integration_ept'],

    # Views

    'data': [
            'data/delivery_fedex.xml',
            'views/shipping_instance_ept_view.xml',
            'views/delivery_carrier_view.xml'],

    # Odoo Store Specific

    'images': ['static/description/shipping-Connector.jpg'],

    # Author

    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'http://www.emiprotechnologies.com',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',

    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'live_test_url': 'https://www.emiprotechnologies.com/free-trial?app=fedex-shipping-ept&version=12&edition=enterprise',
    'price': '149' ,
    'currency': 'EUR',

}
