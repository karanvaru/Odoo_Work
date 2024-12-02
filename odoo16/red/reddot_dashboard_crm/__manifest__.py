# -*- coding: utf-8 -*-
{
    'name': "Reddot Dashboard CRM",
    'summary': """Reddot Dashboard CRM""",
    'author': "Reddot Dashboard CRM",
    'category': 'crm',
    'version': '0.1',
    'author': "Reddot Distribution",
    "website": "https://reddotdistribution.com",
    'depends': [
        'crm',
    ],
    'data': [
        # 'data/lead_send_mail_cron.xml',
        # 'data/lead_close_date_mail_template.xml',
        # 'data/lead_mail_template.xml',
        # 'data/report_automation_config_data.xml',
        'views/dashboard_views.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'reddot_dashboard_crm/static/src/scss/style.scss',
            'reddot_dashboard_crm/static/src/css/dashboard.css',
            'reddot_dashboard_crm/static/src/js/lib/Chart.bundle.js',
            'reddot_dashboard_crm/static/src/xml/crm_dashboard_template.xml',
            'reddot_dashboard_crm/static/src/js/crm_dashboard.js',
        ],
    },
}
