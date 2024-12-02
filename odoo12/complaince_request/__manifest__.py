{
    'name': 'Complaince Request ',
    'version': '12.0.1.0.0',
    'sequence': 10,
    'author': 'RDP',
    'company': 'rdp',
    'website': "https://www.openhrms.com",
    'depends': ['base', 'mail'],
    'data':
    [
        'security/ir.model.access.csv',
        'view/complaince_view.xml',

    ],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
