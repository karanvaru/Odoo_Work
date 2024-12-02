{
    'name': "Finance Audit",
    'version': '12.0.0.1',
    'author': 'RDP',
    'website': 'https://www.rdp.in',
    'summary': 'Finance Audit',
    'description': """
    It is about Finance Audit.
    """,
    'depends': ['base', 'mail'],
    'data': [
        'data/finance_audit_sequence.xml',
        'security/ir.model.access.csv',
        'views/finance_audit.xml'
    ],
    'demo': [],
    'images': [],
    'license': 'OPL-1',
    'installable': 'True',
    # 'application': 'False',
    # 'auto_install': 'False',
}
