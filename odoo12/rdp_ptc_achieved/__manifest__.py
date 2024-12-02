{
    'name': 'PTC Achieved',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'Partner Target Commitment vs Achieved',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     'Partner Target Commitment vs Achieved'
    """,
    'depends': ['base', 'mail'],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/ptc_achieved.xml',
    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,
}
