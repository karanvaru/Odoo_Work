# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale Estimate Customer Portal with Customer Signature',
    'version': '1.1.1',
    'category': 'Sales/Sales',
    'price': 50.0,
    'currency': 'EUR',
    'summary': """Sale Estimate Portal with Digital Signature by Customer""",
    'description': """
This app allows your customer to do a signature on an estimate on the portal of your website.
    """,
    'license': 'Other proprietary',
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/sale_estimate_customer_approve_sign/1339',
    'images': ['static/description/img.png'],
    'support': 'contact@probuse.com',
    'depends': ['sale_estimate_customer_portal','website',
    ],
    'data': [
        'views/sale_estimate.xml',
        'views/sale_estimate_signature_template.xml',
    ],
    'installable': True,
    'auto_install': False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
