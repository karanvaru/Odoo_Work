# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

{
    'name': "CRM Portal Account",
    'summary': """CRM Portal Account""",
    'description': """CRM Portal Account""",
    'version': "0.5",
    'category': "CRM",
    'author': "Kiran Infosoft",
    'website': "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "depends": [
        'crm','crm_checklist'
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizard/assign_lead_partners_view.xml',
        'views/res_partner_view.xml',
        'views/crm_view.xml',
        'views/crm_portal_template.xml',
        'views/bid_details_view.xml',
        'views/assets.xml',
        'data/cron.xml'
    ],
    'application': False,
    'installable': True,
}
