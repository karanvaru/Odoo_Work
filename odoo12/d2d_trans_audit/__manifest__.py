{
    'name': "Accounting Transactions Audit",
    'version': '12.0.0.1',
    'author': 'RDP',
    'website': 'https://www.rdp.in',
    'summary': 'Accounting Transactions Audit',
    'description': """
    It is about Accounting Transactions Audit.
    """,
    'depends': ['base', 'mail'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/trans_audit.xml',
        'views/trans_audit_sequence.xml',
    ],
    'demo': [],
    'images': [],
    'license': 'OPL-1',
    'installable': 'True',
    # 'application': 'False',
    # 'auto_install': 'False',
}
