{
    'name': 'RDP Source Document',
    'version': '12.0.1.0.0',

    'author': 'RDP',
    'company': 'RDP',
    'website': "https://rdp.in",
    'depends': ['stock_account','purchase','sale','account'],
    'data': [
        'data/source_document_action.xml',
        'security/ir.model.access.csv',
        'wizard/update_sale_stock_wizard_view.xml',
        'views/account_move_inherit_view.xml',
    ],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
