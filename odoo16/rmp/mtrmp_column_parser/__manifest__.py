# -*- coding: utf-8 -*-

{
    'name': "Column Parser",
    'summary': """Sales Shop""",
    'description': """Sales Shop""",
    "license": "OPL-1",
    "author": "RMPS",
    "version": "16.0.1.0.1",
    "depends": [
        'stock', 'l10n_in',
        'sale_management', 'delivery'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/column_parser_views.xml',
        'wizard/mtrmp_column_views.xml'
    ],
    'installable': True,
}
