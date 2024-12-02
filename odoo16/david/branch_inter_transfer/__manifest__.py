{
    'name': "Branch Inter Transfer",
    'version': '16.0.4.0.0',
    'summary': """Branch Inter Transfer""",
    'description': """Branch Inter Transfer""",
    'author': 'Kiran Infosoft',
    'company': 'Kiran Infosoft.',
    'depends': ['sh_stock_branch'],
    'data': [
        'security/ir.model.access.csv',
        'data/inter_branch_sequnce.xml',
        'views/inter_branch_transfer_view.xml'
    ],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
