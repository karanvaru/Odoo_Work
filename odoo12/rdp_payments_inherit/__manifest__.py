{
    'name': 'RDP Payment Category',
    'version': '12.0.0.1',
    'summary': 'Payment Category',
    'description': '',
    'category': 'account',
    'author': 'RDP',
    'website': 'rdp.in',
    'license': 'AGPL-3',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/category.xml',
        'views/chart_of_accounts_view.xml'
    ],
    'installable': True,
    'auto_install': False,
}
