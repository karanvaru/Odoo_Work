# -*- coding: utf-8 -*-
{
    'name': "Insurance Management Dashboard",
    'summary': """Insurance Management Dashboard""",
    'description': """
        Insurance Management Dashboard
    """,
    "version": "1.3",
    "category": "Accounting & Finance",
    'author': "Qnomix Technologies",
    "website": "https://www.qnomixtechnologies.com/",
    'license': 'Other proprietary',
    "depends": [
        'qno_insurance_management',
    ],
    'images': ['static/description/img.jpeg'],
    'assets': {
        'web.assets_backend': [
            'qno_insurance_dashboard/static/src/js/insurance_dashboard.js',
            'qno_insurance_dashboard/static/src/xml/insurance_dashboard_view.xml',
            'qno_insurance_dashboard/static/src/scss/style.scss',
        ],
    },

    "data": [
        'views/menu_item.xml',
    ],

    "application": False,
    'installable': True,
}
