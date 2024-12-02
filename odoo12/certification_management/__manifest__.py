{
    'name': "Certification Management",
    'version': '12.0.0.1',
    'author': 'RDP',
    'website': 'https://www.rdp.in',
    'summary': 'Certification Management',
    'description': """
    It is about Certification Management.
    """,
    'depends': ['base', 'mail','hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/certification_management.xml',
        'views/certification_management_sequence.xml'
    ],
    'demo': [],
    'images': [],
    'license': 'OPL-1',
    'installable': 'True',
    # 'application': 'False',
    # 'auto_install': 'False',
}
