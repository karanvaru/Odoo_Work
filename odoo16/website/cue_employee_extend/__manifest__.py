# -*- coding: utf-8 -*-
{
    'name': 'Cue Employee Extend',
    'category': 'Employee',
    'version': '1.1.0',
    'summary': 'This App Is Based On Employee',
    'sequence': -100,
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'description': 'Cue Employee Extend',
    'depends': [
        'base','hr','stock', 'hr_expense'
    ],
    'data': [
        'views/hr_employee_inherit_view.xml',
        'views/stock_move_line_inherit_view.xml',
    ],

    'application': True,
    'license': 'LGPL-3',
    'demo': [],
}
