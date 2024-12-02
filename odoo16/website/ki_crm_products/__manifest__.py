# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

{
    'name': "Crm Products",
    'summary': """Crm Products""",
    'description': """Crm Products""",
    'version': "0.10",
    'category': "crm",
    'author': "Kiran Infosoft",
    'website': "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "depends": [
        'crm', 'sale'
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/crm_lead_inherit.xml'
    ],
    'application': False,
    'installable': True,
}
