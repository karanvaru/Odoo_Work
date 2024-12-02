# -*- encoding: utf-8 -*-

{
    'name': 'CUE Web Profiles',
    'description': 'CUE Web Profiles',
    'category': 'website',
    'sequence': 1000,
    'version': '1.0',
    'depends': ['website', 'web','website_blog'],
    'images': [
    ],
    'data': [
        'data/signup_mail.xml',
        'views/template_reset_password.xml',
        'views/signup_page.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'cue_website_profile/static/scss/login_system_design.scss'
        ],
        'web.assets_frontend_lazy': [
            'cue_website_profile/static/js/signup_page.js',
        ],
    },

    'license': 'LGPL-3',
}
