# -*- coding: utf-8 -*-
{
    'name': 'stock request managment',
    'category' : 'managment',
    'version' : '1.1.0',
    'summary' : 'this app is based on management',
    'sequence' : -100,
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'description' : 'stock request managment',
    'depends':[
        'mail',
        'sale'
    ],
    'images':['static/description/logo.png'],
    'data': [
        'security/ir.model.access.csv',
        'security/stock_request_security.xml',
        'data/stock_request_sequence_data.xml',
        'views/sale_order.xml',
        'views/stock_request.xml',
    ],
    'application': True,
    'license': 'LGPL-3',
    'demo':[],
}