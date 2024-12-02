{
    'name': 'Job Position Open Days',
    'version': '12.0.1.0.0',
    'sequence': -140,
    'author': 'RDP',
    'company': 'rdp',
    'website': "https://www.openhrms.com",
    'depends': ['base', 'hr', 'mail','job_positions'],
    'data': [
        'security/ir.model.access.csv',
        'views/job_position.xml',
        'views/job_opening.xml',

    ],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
