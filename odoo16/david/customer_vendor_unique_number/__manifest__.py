# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Contact / Customer / Supplier / Unique Number",
    'version': '6.1.4',
    'license': 'Other proprietary',
    'category': 'Sales/Sales', 
    'price': 12.0,
    'currency': 'EUR',
    'summary':  """This app generates a number of companies and its contacts in Odoo on creation.""",
    'description': """
This app generates a number of companies and its contacts in Odoo on creation.
Contact / Customer / Supplier / Unique Number
contact unique number
customer unique number
customer number
vendor number
customer identification number
        
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img88.jpg'],
    #'live_test_url': 'https://youtu.be/-7_9nfOn1zU',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/customer_vendor_unique_number/686',#'https://youtu.be/BQ-UYcL6EcA',
    'depends': ['contacts'],
    'data': [
           'data/ir_sequence_data.xml',
           'views/res_partner_view.xml',
            ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
