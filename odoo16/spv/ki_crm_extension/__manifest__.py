# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

{
    'name': "CRM Extension",
    'summary': """CRM Extension""",
    'description': """CRM - Sale order Integration (WON & LOST) with Sale Order Confirmation & Canceled""",
    'version': "0.2",
    'category': "CRM",
    'author': "Kiran Infosoft",
    'website': "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "depends": [
        'crm', 'sale','sale_crm'
    ],
    "data": [
        'security/ir.model.access.csv',
        'wizard/crm_lead_won.xml',
        'wizard/crm_lead_lost_views.xml',
        'views/crm_lead.xml',
        'views/sale_order.xml'
    ],
    'application': False,
    'installable': True,
}
