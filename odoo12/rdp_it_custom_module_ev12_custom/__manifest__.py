{
    'name': 'RDP IT Custom',
    'version': '17.0.0.1',
    'author': 'RDP',
    'category': 'Customizations',
    'depends': ['base', 'mail',
                ],
    'data': [
        'security/ir.model.access.csv',
        'views/rdp_it_custom.xml',
        'views/record_category.xml',
        'views/record_type.xml',
        
    ],
    'images': ['rdp_it_custom_module_ev12_custom,static/description/icon.png'],

    'installable': True,
    'application': True,
    'auto_install': False,
}
