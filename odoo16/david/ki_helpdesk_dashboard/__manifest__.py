

{
    'name': "Website HelpDesk Dashboard V16",
    'description': """Helpdesk Support Ticket Management Dashboard""",
    'summary': """Website HelpDesk Dashboard Module Brings a Multipurpose"""
               """Graphical Dashboard for Website HelpDesk module""",
    'version': '0.4',
    'author': "Kiran Infosoft",
    "website": "https://www.kiraninfosoft.com",
    'company': 'Kiran Infosoft',
    'maintainer': 'Kiran Infosoft',
    'category': 'Website',
    'depends': ['website_helpdesk_support_ticket', 'base'],
    'data': [
        'views/dashboard_view.xml',
        'views/dashboard_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ki_helpdesk_dashboard/static/src/css/dashboard.css',
            'ki_helpdesk_dashboard/static/src/js/lib/Chart.bundle.js',
            'ki_helpdesk_dashboard/static/src/xml/dashboard_view.xml',
            'ki_helpdesk_dashboard/static/src/js/dashboard_view.js',
        ],
    },
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
