# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Contract Extension",
    'summary': """""",
    'description': "",
    "version": "14.0",
    "category": "Contract",
    'author': "Kiran Infosoft",
    "website": "https://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "depends": [
         'account',
         'contract',
         'l10n_in',
    ],
    "data": [
            'views/contract_line_view.xml',
            'views/contract_view.xml',
            'views/sale_order_line_view.xml',
            'views/sale_order_view.xml',
            'views/menu_item.xml',
            'report/report.xml',
            'report/template_report.xml',
    ],
    'installable': True,
}
