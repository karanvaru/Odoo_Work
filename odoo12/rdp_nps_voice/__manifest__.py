{
    'name': 'RDP NPS Voice',
    'version': '12.0.1.0.0',
    'sequence': 10,
    'author': 'RDP',
    'company': 'RDP',
    'website': "https://www.rdp.in",
    'depends': ['base', 'mail','sale'],
    'data': [
        # 'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/nps_voice.xml',
    ],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
