# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################
{
    'name': "Vendor Product List",
    'category': 'Purchases',
    'version': '16.0.1.0',
    'author': 'Equick ERP',
    'description': """
        This Module user to see vendor product list.
    """,
    'summary': """purchase vendor pricelist vendor product list vendors product list vendor products list supplier product list partner product list""",
    'depends': ['purchase'],
    'price': 7,
    'currency': 'EUR',
    'license': 'OPL-1',
    'website': "",
    'data': [
        'views/res_partner_view.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: