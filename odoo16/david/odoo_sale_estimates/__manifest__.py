# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Sale Estimates to Customer",
    'version': '8.2.7',
    'price': 49.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This module allow you to create estimate and send your customer. And create quotation from estimates.""",
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
    'category' : 'Sales/Sales',
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/se11.jpg'],
    #'live_test_url': 'https://youtu.be/2zlLuwSgBdQ', #'https://youtu.be/ah0FZVSjlTk',
    # 'live_test_url': 'https://probuseappdemo.com/probuse_apps/odoo_sale_estimates/670',#'https://youtu.be/sz3NwnSDomk',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/odoo_sale_estimates/1268',
    'depends': [
                'sale_management',
                'sale',
                ],
    'data':[
        'security/ir.model.access.csv',
        'security/estimate_security.xml',
        'report/estimate_report.xml',
        'data/estimate_sequence.xml',
        'data/estimate_mail.xml',
        'views/sale_estimate_views.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
