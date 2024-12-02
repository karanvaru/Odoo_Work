{
    'name': 'Ki Job Application',
    'version': '17.0.2.8',
    'license': "OPL-1",
    'category': 'Human Resources/Recruitment',
    'author': 'Kiran Infosoft.',
    'website': "http://www.kiraninfosoft.com",
    'summary': '''
        This module allows to user/candidate and employee to fill the job application in details from portal. | Job Applicant | Job Portal | Submit Job Application | HR Job Application | HR Recruitment | Job Recruitment | Job Portal - Online Job application
    ''',
    'description': '''
        module allows to user/candidate and employee to fill the job application in details from portal
    ''',
    'depends': [
'base',
        'hr',
        'hr_recruitment',
        'website_hr_recruitment',
        'job_portal_kanak'
    ],
    'data': [

        'security/ir.model.access.csv',
        'data/recruitment_document_type_data.xml',
        'views/hr_applicant_view.xml',
        'views/employe_template_view.xml',
        'views/recruitment_document_type_view.xml',
        'views/job_portal_headers_details_view.xml',
        'views/recruiting_agent_view.xml',
        'views/menu_item.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ki_job_portal_kanak_extends/static/src/scss/custom.scss',
            # 'ki_job_portal_kanak_extends/static/src/js/job_portal.js',
        ],
    },
    'images': ['static/description/banner.gif'],
    'installable': True,
    'price': 75,
    'currency': 'EUR',
}
