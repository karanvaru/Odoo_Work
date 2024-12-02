# -*- coding: utf-8 -*-
{
    'name': 'Accounting Dashboard',
    'category': 'Accounting',
    'version': '1.1.0',
    'summary': 'This App Is Based On Accounting',
    'sequence': -100,
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'description': 'Accounting Dashboard',
    'depends': ['base', 'account','web','base_accounting_kit','dynamic_accounts_report', 'hr_payroll_account_community'],
    'data': [
    ],
    'data': [
        'views/account_configuration.xml',
        'views/hr_payslip_views.xml',
        'views/sale_order_line_views.xml',
        # 'wizard/reports_config_view.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'ki_accounting_dashboard_extends/static/src/js/accound_dashbord.js',
            'ki_accounting_dashboard_extends/static/src/scss/style.scss',
            'ki_accounting_dashboard_extends/static/src/xml/dashbord_template.xml',
        ],
    },


    'application': True,
    'license': 'LGPL-3',
    'demo': [],
}
