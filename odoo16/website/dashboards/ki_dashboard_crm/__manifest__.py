{
    'name': 'Ki Dashboard CRM',
    'version': '16.0.2.0.9',
    'category': 'CRM',
    'summary': """ CRM Dashbord""",
    'description': """ CRM Dashbord """,
    'author': 'Kiran Infosoft',
    'website': "http://www.kiraninfosoft.com",
    'company': 'Kiran Infosoft',
    'depends': ['crm'],
    'data': [
        'views/dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ki_dashboard_crm/static/src/scss/style.scss',
            'ki_dashboard_crm/static/src/css/dashboard.css',
            'ki_dashboard_crm/static/src/js/lib/Chart.bundle.js',
            'ki_dashboard_crm/static/src/xml/crm_lead.xml',
            'ki_dashboard_crm/static/src/js/crm_lead.js',
        ],
    },
    'license': 'LGPL-3',
    'images': ['static/description/banner.gif'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
