{
    'name': "Hiring Sources",
    'version': '12.0.0.1',
    'author': 'RDP',
    'website': 'https://www.rdp.in',
    'summary': 'Hiring Sources',
    'description': """
    It is about Hiring Sources.
    """,
    'depends': ['base', 'mail','hr_recruitment'],
    'data': [
        'security/ir.model.access.csv',
        'views/hiring_sources.xml',
        'views/hiring_sources_sequence.xml',
    ],
    'demo': [],
    'images': [],
    'license': 'OPL-1',
    'installable': 'True',
    # 'application': 'False',
    # 'auto_install': 'False',
}
