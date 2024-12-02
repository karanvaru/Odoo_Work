{
    'name': 'Canisters And Medicines Custom Module',
    'version': '15.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': ' Custom App',
    'sequence': '10',
    'depends': ['base', 'sale','stock','mrp'],
    'data': [

        # 'security/ir.model.access.csv',
        'views/custom_view.xml',
        # 'wizards/mo.xml',
    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}