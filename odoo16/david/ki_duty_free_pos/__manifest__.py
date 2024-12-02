# -*- coding: utf-8 -*-
{
    'name': "Point of sale extension",
    'summary': """Point of sale extension""",
    'description': """Point of sale extension""",
    'author': "Kiran Infosoft",
    'website': "http://www.kiraninfosoft.com",
    'category': 'Point Of Sale',
    'version': '2.5',
    'depends':
        [
            'point_of_sale',
            'pos_payment_layout'
        ],
    'data': [
        'reports/duty_free_pos_reports.xml',
        'views/pos_order_view.xml',
        'views/view_res_partner.xml',
        'views/pos_config.xml'

    ],
    "assets": {
        "point_of_sale.assets": [
            "ki_duty_free_pos/static/src/js/**/*",
            '/ki_duty_free_pos/static/src/css/pos.scss',
            "ki_duty_free_pos/static/src/xml/extend_button.xml",
            "ki_duty_free_pos/static/src/xml/extend_popup.xml",
            "ki_duty_free_pos/static/src/xml/extend_pos_payment_screen.xml",
            "ki_duty_free_pos/static/src/xml/PartnerDetailsEdit.xml",
            "ki_duty_free_pos/static/src/xml/PartnerLine.xml",
            'ki_duty_free_pos/static/src/xml/PaymentScreenStatus.xml'
        ],
    },
    'installable': True,
    'application': True,
}
