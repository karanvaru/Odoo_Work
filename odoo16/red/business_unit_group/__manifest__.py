# -*- coding: utf-8 -*-
{
    'name': "Business Units",

    'summary': """
        Define Business Units and Business Unit Groups""",

    'author': "Reddot Distribution",

    
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'hr', 'sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/business_unit.xml',
        'views/product.xml'
    ],
}
