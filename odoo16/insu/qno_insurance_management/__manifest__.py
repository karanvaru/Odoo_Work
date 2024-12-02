# -*- coding: utf-8 -*-
# Part of Qnomix Technologies. See LICENSE file for full copyright and licensing details.
{
    'name': "Insurance Management",
    'summary': """Insurance Management""",
    'description': """
        Insurance Management
    """,
    "version": "1.3",
    "category": "Accounting & Finance",
    'author': "Qnomix Technologies",
    "website": "https://www.qnomixtechnologies.com/",
    'license': 'Other proprietary',
    "depends": [
        'sale_management',
        'stock',
        'partner_firstname',
        'partner_middlename'
    ],
    'images': ['static/description/img.jpeg'],
    "data": [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequence_data.xml',
        'data/insurance_policy_stage_change.xml',
        'data/customer_policy_expiry_cron.xml',
        'data/mail_data.xml',
        'data/suggested_product_mail.xml',
        'data/cusotmer_suggested_product_mail.xml',
        'wizard/sale_policy_confirm_wizard_view.xml',
        'wizard/sale_policy_detail_wizard_view.xml',
        'wizard/claim_process_wizard_view.xml',
        'wizard/raise_query_wizard_view.xml',
        'wizard/claim_approve_wizard_view.xml',
        'wizard/claim_reject_wizard_view.xml',
        'wizard/add_payment_bank_view.xml',
        'reports/quatation_order_report.xml',
        'reports/sale_quatation_report.xml',
        'views/partner_relative.xml',
        'views/partner/agent_view.xml',
        'views/partner/insurance_company_view.xml',
        'views/partner/customer_view.xml',
        'views/product_category_view.xml',
        'views/product_view.xml',
        'views/sale_order_view.xml',
        'views/insurance_policy_views.xml',
        'views/claim_details_views.xml',
        'views/claim_stage.xml',
        'views/menu.xml'
    ],
    "application": False,
    'installable': True,
}
