# -*- coding: utf-8 -*-
{
    'name': "Pos Extend",
    'summary': """Pos Extend""",
    'description': """Pos Extend""",
    'author': "Kiran Infosoft",
    'website': "http://www.kiraninfosoft.com",
    'category': 'Point Of Sale',
    'version': '1.0',
    'depends':
        [
            'point_of_sale',
        ],
    'data': [
        'reports/report.xml',

    ],
    "assets": {
        "point_of_sale.assets": [
            # "ki_duty_free_pos/static/src/js/extend_button.js",
            # "ki_duty_free_pos/static/src/js/extend_popup.js",
            # "ki_duty_free_pos/static/src/js/models.js",
            # "ki_duty_free_pos/static/src/js/ProductScreen.js",
            "ki_pos_payment_button/static/src/js/**/*",
            # "ki_duty_free_pos/static/src/jss/extend_button.jss",
            # "ki_duty_free_pos/static/src/jss/ProductScreen.jss",
            "ki_pos_payment_button/static/src/xml/extend_pos_payment_screen.xml",
        ],
    },
    'installable': True,
    'application': True,
}
