{
    'name': "Source Master",
    'version': '12.0.0.2',
    'author': 'RDP',
    'website': 'https://www.rdp.in',
    'summary': 'Source Master',
    'description': """
    It is about Source Master.
    """,
    'depends': ['base', 'mail', 'amazon_ept'],
    'data': [
        'security/ir.model.access.csv',
        'views/sourcing_master.xml',
        'views/sourcing_master_sequence.xml',
    ],
    'demo': [],
    'images': [],
    'license': 'OPL-1',
    'installable': 'True',
    # 'application': 'False',
    # 'auto_install': 'False',
}
