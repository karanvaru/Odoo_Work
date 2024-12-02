{
    'name': 'Custom Model',
    'version': '17.0.0.1.2',
    'author': 'RDP',
    'category': 'Customizations',
    'depends': ['base', 'mail',
                ],
    'data': [
        'security/ir.model.access.csv',
        'views/custom_model.xml',
        'views/transaction_category.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
