# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'HR Exit Process Management',
    'version': '1.1.1',
    'price': 15.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'images': ['static/description/image1.jpg'],
    'live_test_url': 'https://youtu.be/WxKofWvXqjk',
    'category': 'Human Resources',
    'summary': 'Employee Out/Exit/Termination Process Management',
    'description': """
        Employee Exit process:
            ---> Configure CheckLists
            ---> Employee Exit Request
            ---> Employee Exit Checklists
            ---> Print Employee Exit Report 

Tags:
exit process
employee exit process
employee termination process
employee leave process
employee leave company
employee exit company
hr exit process
human resource exit process
checklist for exit process
Termination terminate
            """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'depends': ['hr', 'hr_contract', 'survey', 'calendar','rdp_employee_inherited'],
    'data': [
            'data/created_status_template.xml',
            'data/created_hr_mail_employee_exit_template.xml',
            'data/manager_approval_conformation_to_employee_exit_request.xml',
            'data/manager_approval_conformation_to_hr_exit_request.xml',
            'data/hr_manager_approval_conformation_to_employee_exit_request.xml',
            'data/hr_manager_approval_conformation_to_manager_exit_request.xml',
            'data/fnf_comp_to_employee_mail.xml',
            'data/fnf_comp_to_manager_mail.xml',
            'security/hr_exit_security.xml',
            'security/ir.model.access.csv',
            'views/hr_exit_view.xml',
            'report/hr_exit_process_report.xml',
             ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
