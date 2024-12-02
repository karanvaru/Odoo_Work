# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Customer Vendor Unique Number Extend",
    'summary': """Customer Vendor Unique Number Extend""",
    'description': """Customer Vendor Unique Number Extend""",
    "version": "1.3.0",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "depends": [
        'customer_vendor_unique_number',
        'contacts',
    ],
    "data": [
        'data/set_number_server_action.xml',
        'views/customer_vendor_unique_number.xml',
    ],
    "application": False,
    'installable': True,
}
