# -*- coding: utf-8 -*-
{
    'name': 'Odoo Easy Search, global search, quick search',
    'summary': 'Search any data in Odoo. quick and easy. all data search. global search. fast search easy search search',
    'author': "Simple Apps",
    'license': 'OPL-1',
    'version': '13.0',
    'description': """User can easily search any data or record from Odoo.
The entered query will be searched in all possible objects.  
""",
    'category': 'Tools',
    'depends': ['web'],
    'data': [
        'security/search_security.xml',
        'security/ir.model.access.csv',
        'views/search_views.xml',
        'views/all_search_template.xml',
    ],
    'qweb': [
        'static/src/xml/all_search.xml'
    ],
    'images': ['static/description/show.gif'],
    'price': 29,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False
}

