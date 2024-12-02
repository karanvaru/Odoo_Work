# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Spv Sale Extension",
    'summary': """spv Sale Extension""",
    'description': """spv Sale Extension""",
    "version": "1.8.0",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "depends": [
        'sale',
        'base',
        'ki_sale_term_conditions',
        'ki_spv_costing',
    ],
    "data": [
        'security/ir.model.access.csv',
        'reports/solar_power_plant_proposal.xml',
        'views/sale_order_extensions.xml',
        'views/document_required.xml',
        'views/contact_inherit_view.xml',
    ],
    "application": False,
    'installable': True,
}
