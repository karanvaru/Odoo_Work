# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Odoo Sale Estimates Extend",
    'summary': """Odoo Sale Estimates Extend""",
    'description': """Odoo Sale Estimates Extend""",
    "version": "1.4",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'OPL-1',
    "depends": [
        'odoo_sale_estimates',
        'ki_sale_invoice_sequence'
    ],
    "data": [
        'report/estimate_report_extend.xml',
        'views/sale_estimate_inherit_view.xml',
        'views/quote_sequence_mapping_inherit_view.xml',
    ],
    "application": False,
    'installable': True,
}
