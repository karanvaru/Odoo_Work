{
    'name': 'Repair Inherited',
    'version': '12.0.0.1',
    'sequence': -140,
    'author': 'RDP',
    'company': 'RDP',
    'depends': ['base','repair','mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/repair_inherited.xml',


    ],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
