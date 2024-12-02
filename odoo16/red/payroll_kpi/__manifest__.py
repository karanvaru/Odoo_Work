# -*- coding: utf-8 -*-
{
    'name': "Payroll Based on KPIs",

    'summary': """
        # 10 percent of basic wage is determined by the KPI provided by department managers """,

    'description': """
        10 percent of basic wage is determined by the KPI provided by department managers """,


    'author': "Red Dot Distribution",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Technical',
    'version': '0.1',
    'license': 'LGPL-3',
    # any module necessary for this one to work correctly
    'depends': ['hr_payroll', 'hr_ke', 'hr_appraisal'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/kpi_security.xml',
        'views/kpi.xml',
        'views/kpi_config.xml',
        'views/employee_score.xml',
        'wizard/kpi_employee.xml',
        'data/gross_deduction.xml',
        'data/emails.xml',
        'data/server_actions.xml',
        
    ],

    'assets': {
        'web.assets_backend': [
            'payroll_kpi/static/src/css/kpi.css',
            'payroll_kpi/static/src/js/kpi.js',
        ]
    }
}
