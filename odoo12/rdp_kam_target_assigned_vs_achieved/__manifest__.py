{
    'name': 'RDP KAM Target Assigned VS Achieved',
    'version': '12.0.1.0.0',
    'sequence': -140,
    'author': 'RDP',
    'company': 'rdp',
    'website': "https://www.openhrms.com",
    'depends': ['base', 'sale', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/kam_target.xml',
        'data/sequence.xml',


    ],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
