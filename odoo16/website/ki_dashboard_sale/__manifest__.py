{
    'name': 'Ki Dashboard Sale',
    'version': '16.0.2.0.9',
    'category': 'Salse',
    'summary': """ Sales Dashbord""",
    'description': """ Sales Dashbord """,
    'author': 'Kiran Infosoft',
    'website': "http://www.kiraninfosoft.com",
    'company': 'Kiran Infosoft',
    'depends': ['sale'],
    'data': [
        'views/dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ki_dashboard_sale/static/src/scss/style.scss',
            'ki_dashboard_sale/static/src/css/dashboard.css',
            'ki_dashboard_sale/static/src/js/lib/Chart.bundle.js',
            'ki_dashboard_sale/static/src/xml/sale_dashbord.xml',
            'ki_dashboard_sale/static/src/js/sale_order_dashbord.js',
        ],
    },
    'license': 'LGPL-3',
    'images': ['static/description/banner.gif'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
