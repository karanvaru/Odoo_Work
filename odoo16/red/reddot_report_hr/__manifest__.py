# -*- coding: utf-8 -*-
{
    'name': "Reddot Report For HR",
    'summary': """Reddot Report  For HR""",
    'author': "Reddot Report  For HR",
    'category': 'Uncategorized',
    'version': '1.1',
    'author': "Reddot Distribution",
    "website": "https://reddotdistribution.com",
    'depends': [
        'hr',
        'base',
        'mail',
        'hr_contract',
        'hr_payroll',
        'hr_attendance',
        'hr_holidays',
        'hr_expense',
        'payroll_kpi',
        'dev_hr_loan',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_inherit_view.xml',
        'views/hr_leave_type_view.xml',
        'data/send_employee_mail_cron.xml',
        'data/demographics_email_template.xml',
        'data/contract_report_mail_template.xml',
        'wizard/hr_contract_report_wizard_view.xml',
        'wizard/hr_employee_report_wizard_view.xml',
        'wizard/leave_wizard_report_view.xml',
        'wizard/contact_report_wizard_view.xml',
        'wizard/employee_demographic_summary_wizard.xml',
        'wizard/loan_report_wizard_view.xml',
        'wizard/kpi_performance_report_wizard_view.xml',
        'wizard/attendance_report_summary_wizard_view.xml',
        'wizard/helpdesk_report_wizard_view.xml',
    ],
}
