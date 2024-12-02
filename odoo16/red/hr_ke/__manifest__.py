# -*- coding: utf-8 -*-
{
    'name': "Payroll and HR System For Kenya",
    'license': 'OPL-1',
    'support': 'support@optima.co.ke',

    'summary': """
        Automated Payroll and HR system customized for Kenya, with KRA reports and automated Tax Returns """,

    'description': """
        In this module, we are adding Kenya specific HR details and requirements for processing payroll. NSSF, NHIF, Next Of Kin, PAYE, HELB and others
    """,
    'images': ['static/description/hr.png'],
    'author': "Optima ICT Services LTD",
    'website': "http://www.optima.co.ke",
    'price': 351,
    'currency': 'EUR',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '16.0.0.0.6',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'hr_contract',  'hr_payroll', "purchase",
    'send_payslips_by_email', 'attachment_indexation',
    'hr_contract_types', 'hr_work_entry_contract'],
    'external_dependencies': {'python': ['openpyxl']},

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',      
        'data/overtime_data.xml',
        'data/salary_advance_data.xml',
        'data/categories_data.xml',
        'data/salary_structure_data.xml',
        'data/rules_data.xml',
        'data/benefits_data.xml',
        'data/cash_allowances_data.xml',
        'security/rules.xml',
        'data/deductions_data.xml',
        'data/tax_relief_data.xml',
        'data/hr_contract_data.xml',
        # 'views/overtime_view.xml',
        'views/res_users.xml',
        'views/advance_view.xml',
        'views/contract_view.xml',
        'views/hr_payroll_account_views.xml',
        'views/hr_view.xml',
        'views/res_config_view.xml',
        
        # 'views/abseenteesm.xml',
        'wizard/p9.xml',
        'report/templates.xml',
        'report/main.xml',
        'report/misc.xml',
        'report/report.xml'
    ],
    # only loaded in demonstration mode
    'installable': True,
    'auto_install': False,
    'application': True,
}
