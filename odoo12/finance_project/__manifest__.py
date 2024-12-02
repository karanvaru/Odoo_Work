{
    'name': "RDP Finance Task Requirements",
    'version': '1.1',
    'author': 'RDP',
    'website': 'https://www.rdp.in',
    'summary': 'RDP Finance Task Requirements',
    'description': """
    It is about RDP Finance Task Requirements.
    """,
    'depends': ['base', 'mail'],
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/finance_project.xml'


    ],
    'demo': [],
    'images': [],
    'license': 'OPL-1',
    'installable': 'True',
    # 'application': 'False',
    # 'auto_install': 'False',
}
