# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Odoo Job Applicants Portal",
    'version': '1.2',
    'currency': 'EUR',
        'price': 49.0,

    'license': 'Other proprietary',
    'category': 'Human Resources',
    'summary': """This module allow your candidate and applicants apply from portal and check status of applications.""",
    'description': """
Odoo Job Recruitment  Portal
This module allow responsible user can Apply for Jobs and see there application from My Account Page.
Also Send Attachment and Messages To Applications.
Odoo Job Recruitment Portal
Odoo Job Recruitment Applications
Odoo Applicaitons
Job Recruitment Portal
Recruitment Applications
Applications
Job Applications
My Applications
Applications
Send Attachment on Applicaitons
job portal
Recruitment portal
applicant portal
job positions portal
Odoo Job Recruitment Portal
candidate portal
apply now
odoo job
odoo job portal
odoo job apply
job odoo
applicant portal job
apply online
job apply online
online-job-portal-recruiters
online job portal
job search
job apply


    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpeg'],
#    #'live_test_url': 'https://youtu.be/L1XzYc2JxBE',
    #'live_test_url': 'https://youtu.be/OlMKPFwXcec',
    'depends': [
                'hr_recruitment',
                'portal',
                # 'hr_applicant_recruitment',
                'website_hr_recruitment',
                ],
    'data':[

            'views/hr_recruitment.xml',

    ],
'qweb': [
        'static/css/job_application_form.css',  # Include your template if it contains QWeb code
    ],
    'installable' : True,
    'application' : False,

    'assets': {
        'web.assets_frontend': [
            'odoo_recruitment_job_portal/static/css/job_application_form.css',
        ],
    },
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
