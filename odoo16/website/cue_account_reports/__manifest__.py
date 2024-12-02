# -*- coding: utf-8 -*-
{
    'name': 'Cue Account Reports',
    'category': 'Account',
    'version': '1.1.0',
    'summary': 'This App Is Based On Account',
    'sequence': -100,
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'description': 'Cue Account',
    'depends': [
        'account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sale_summary_filter_wizard_view.xml',
    ],

    'application': True,
    'license': 'LGPL-3',
    'demo': [],
}
