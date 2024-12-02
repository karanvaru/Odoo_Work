# -*- coding: utf-8 -*-
{
    'name': "Reddot Dashboard HR",

    'summary': """Reddot Dashboard""",

    'author': "Kiran Infosoft",

    'category': 'Uncategorized',
    'version': '0.1',
    'website': "http://www.kiraninfosoft.com",
    'depends': ['hr','web','hr_contract'],

    'data': [
        'security/ir.model.access.csv',
        'data/server_actions.xml',
        'data/report_configuration.xml',
        'views/dashboard_views.xml',
        # 'views/hr_contract_history_view.xml',
        'views/hr_report_configuration_view.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'reddot_dashboard_hr/static/src/scss/style.scss',
            'reddot_dashboard_hr/static/src/css/dashboard.css',
            'reddot_dashboard_hr/static/src/js/lib/Chart.bundle.js',
            'reddot_dashboard_hr/static/src/xml/hr_dashboard_template.xml',
            'reddot_dashboard_hr/static/src/js/hr_dashboard.js',
        ],
    },
}
