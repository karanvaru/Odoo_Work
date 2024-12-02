{
    'name': "RDP Exit 14 ",
    'version': '12.0.0.1',
    'author': 'RDP',
    'website': 'https://www.rdp.in',
    'summary': 'RDP Exit 14',
    'description': """
    It is about RDP Exit 14.
    """,
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/rdp_exit14.xml',
        'views/rdp_exit14_sequence.xml',
    ],
    'demo': [],
    'images': [],
    'license': 'OPL-1',
    'installable': 'True',
    # 'application': 'False',
    # 'auto_install': 'False',
}
