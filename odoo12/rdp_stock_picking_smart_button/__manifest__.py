{
    'name': 'Stock picking Smart Button',
    'version': '12.0.1.0.0',
    'sequence': -190,
    'author': 'RDP',
    'company': 'RDP Workstation Pvt Ltd',
    'website': "https://www.openhrms.com",
    'depends': ['base', 'hr', 'mail','stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/inventory_smart_button.xml',


    ],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
