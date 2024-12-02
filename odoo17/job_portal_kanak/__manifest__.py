# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

{
    'name': 'Job Application',
    'version': '17.0.1.2',
    'license': "OPL-1",
    'category': 'Human Resources/Recruitment',
    'author': 'Kanak Infosystems LLP.',
    'website': 'https://kanakinfosystems.com',
    'summary': '''
        This module allows to user/candidate and employee to fill the job application in details from portal. | Job Applicant | Job Portal | Submit Job Application | HR Job Application | HR Recruitment | Job Recruitment | Job Portal - Online Job application
    ''',
    'description': '''
        module allows to user/candidate and employee to fill the job application in details from portal
    ''',
    'depends': [
        'hr',
        'hr_recruitment',
        'website_hr_recruitment'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/hr_recruitment_views.xml',
        'views/employee_template.xml',
        'views/hr_employee_notebook_view.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'job_portal_kanak/static/src/scss/custom.scss',
            'job_portal_kanak/static/src/js/job_portal.js',
        ],
    },
    'images': ['static/description/banner.gif'],
    'installable': True,
    'price': 75,
    'currency': 'EUR',
}
