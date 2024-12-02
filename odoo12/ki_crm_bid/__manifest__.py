# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

{
    'name': "CRM Bid Account",
    'summary': """CRM Bid Account""",
    'description': """CRM Bid Account""",
    'version': "0.15",
    'category': "CRM",
    'author': "Kiran Infosoft",
    'website': "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "depends": [
        'crm','portal','ki_crm_portal','website','base','web_google_maps'
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/crm_bid_view.xml',
        'views/assets.xml',
        'views/crm_portal_template.xml',
        'views/crm_lead_view.xml',
        'views/res_users_view.xml',
        'views/crm_portal_view.xml',
        'security/security.xml',

    ],
    'application': False,
    'installable': True,
}
