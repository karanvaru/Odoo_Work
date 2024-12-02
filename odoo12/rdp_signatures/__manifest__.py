{
    'name': 'RDP Signatures',
    'version': '12.0.1.0.0',

    'author': 'RDP',
    'company': 'RDP',
    'website': "https://rdp.in",
    'depends': ['base','sign','mail'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/signature.xml',

    ],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
