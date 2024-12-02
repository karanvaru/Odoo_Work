# -*- coding: utf-8 -*-
{
    'name': "Point of sale extension for change labels",
    'summary': """Point of sale extension for change labels""",
    'description': """Point of sale extension for change labels""",
    'author': "Kiran Infosoft",
    'website': "http://www.kiraninfosoft.com",
    'category': 'Point Of Sale',
    'version': '1.0',
    'depends':
        [
            'point_of_sale',
        ],
    'data': [
    ],
    "assets": {
        "point_of_sale.assets": [
            "ki_pos_extension/static/src/xml/extend_button.xml",
        ],
    },
    'installable': True,
    'application': True,
}
