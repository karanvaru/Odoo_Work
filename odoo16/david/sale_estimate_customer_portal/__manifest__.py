# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': 'Sale Estimate Show Customer Portal',
    'version': '5.1.2',
    'currency': 'EUR',
    'price': 49.0,
    'license': 'Other proprietary',
    'summary': 'This app allow you to create subcontractor job work order in system and allow subcontractor to view jobs in portal.',
    'description': """
Odoo Sale Estimates
This module create and send estimate to customer and create quotation
create and send estimate to customer
create estimate
send estimate
create estimate
send estimate
Sales/Sales/Estimates
Estimates
estimates
estimate
sale estimate
sales estimate
sale estimates
Sales Estimates Creation and Quote
sales estimates
    
    """,
    'category' : 'Sales',
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'https://www.probuse.com',
    'depends': [
                'portal',
                #'website',
                'odoo_sale_estimates',
                ],
    'support': 'contact@probuse.com',
    'images': ['static/description/image.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/sale_estimate_customer_portal/668',#'https://youtu.be/Isx_DhTFtvk',
    'data': [
        'security/ir.model.access.csv',
        'security/estimate_security.xml',
        'views/sale_estimate_template.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
