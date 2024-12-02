{
    'name': 'RDP Purchase',
    'version': '12.0.1.0.0',
    'sequence': -140,
    'author': 'RDP',
    'company': 'RDP',
    'website': "https://www.openhrms.com",
    'depends': ['base', 'hr', 'mail','purchase'],
    'data': [
        'views/purchase.xml',


    ],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
