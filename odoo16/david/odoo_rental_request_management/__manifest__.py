# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Product Rental Request Management",
    'currency': 'EUR',
    'price': 299.0,
    'version': '8.1.2',
    'summary': """This app allow rental management business for Product/Item/Equipment/Vehicles.""",
    'description': """
odoo rental
rental management
rental request
product rent
rent product
rental product
rental app
odoo rental app
rental module


    """,
    'license': 'Other proprietary',
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/odoo_rental_request_management/871',#'https://youtu.be/N7jBU42EwW0',
    'category' : 'Website/Sale',
    'depends': [
        'website',
        'sale',
    ],
    'assets': {
        'web.assets_frontend': ['odoo_rental_request_management/static/src/js/rental_product_request.js',]
    },
    'data':[
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/product_template_views.xml',
        'views/rental_request_template_view.xml',
        'views/payment_terms_view.xml',
        'views/sale_order_portal_template_view.xml',
        # 'report/sale_order_report_template_view.xml',
        'views/rental_pricing_report_views.xml',
        'views/drop_options_views.xml',
        'views/sale_order_line_report_view.xml',
        'views/menu_items.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
