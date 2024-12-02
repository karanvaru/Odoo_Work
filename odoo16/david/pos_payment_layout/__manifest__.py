# -*- coding: utf-8 -*-

{
    'name': "Pos payment Layout",
    'description': """
        Layout Customization on payment screen
    """,
    'author': "kiran infosoft",
    'website': "http://erp.kiraninfosoft.in/",
    'category': 'Sales/Point of Sale',
    'version': '16.0.1.0',
    'depends': ['point_of_sale'],
    # 'data': [],
    'assets': {
        'point_of_sale.assets': [
            ('after',"point_of_sale/static/src/xml/**/PaymentScreen.xml","pos_payment_layout/static/src/xml/PaymentScreen.xml"),
            "/pos_payment_layout/static/src/scss/payment_screen.scss"
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
