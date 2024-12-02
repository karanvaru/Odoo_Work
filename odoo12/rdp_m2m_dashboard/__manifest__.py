{
    'name': 'M2M Dashboard',
    'version': '12.0.1.0.0',
    'sequence': -190,
    'author': 'RDP',
    'company': 'rdp',
    'website': "https://www.openhrms.com",
    'depends': ['base','hr','mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/m2m_details_view.xml',
        'data/data.xml'

    ],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
