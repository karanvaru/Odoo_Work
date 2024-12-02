# -*- coding: utf-8 -*-
{
    'name': "Reddot Commission",

    'summary': """Reddot Rommission""",

    'author': "Kiran Infosoft",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['hr', 'sale', 'business_unit_group','hr_contract'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'data/division_level.xml',
        'data/sequence.xml',
        'wizard/commission_config_line_allocation_wizard.xml',
        'wizard/commission_history_exception_reason_wizard_view.xml',
        'wizard/generate_commssion_wizard_view.xml',
        'reports/employee_contract_commission_report.xml',
        'views/commission_history_view.xml',
        'views/commission_line_view.xml',
        'views/sale_order.xml',
#         'views/commission_rule_view.xml',
        'views/employee.xml',
        'views/res_company_view.xml',
        'views/commission_target_percentage_sheet_view.xml',
        'views/commission_config_plan_view.xml',
        'views/commission_term_condition_view.xml',
        'views/hr_contract_inherit_view.xml',
        'views/employee_send_mail.xml',
        'views/contract_verification_template.xml',
        'views/menu_item.xml',
    ],
}
