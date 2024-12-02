{
    'name': 'Ki Dashboard Purchase',
    'version': '16.0.2.0.9',
    'category': 'Purchase',
    'summary': """ Purchase Dashbord""",
    'description': """ Purchase Dashbord """,
    'author': 'Kiran Infosoft',
    'website': "http://www.kiraninfosoft.com",
    'company': 'Kiran Infosoft',
    'depends': ['purchase'],
    'data': [
        'views/dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ki_dashboard_purchase/static/src/scss/style.scss',
            'ki_dashboard_purchase/static/src/css/dashboard.css',
            'ki_dashboard_purchase/static/src/js/lib/Chart.bundle.js',
            'ki_dashboard_purchase/static/src/xml/purchase_dashbord.xml',
            'ki_dashboard_purchase/static/src/js/purchase_order_dashbord.js',
        ],
    },
    'license': 'LGPL-3',
    'images': ['static/description/banner.gif'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
