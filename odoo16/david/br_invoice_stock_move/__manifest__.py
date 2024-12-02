{
    'name': "Stock Picking From Invoice",
    'version': '16.0.4.0.0',
    'summary': """Stock Picking From Customer/Supplier Invoice""",
    'description': """This module makes it possible to pick up stock from a customer or supplier invoice.""",
    'author': 'Banibro IT Solutions Pvt Ltd.',
    'company': 'Banibro IT Solutions Pvt Ltd.',
    'website': 'https://banibro.com',
    'category': 'Accounting',
    'depends': ['base', 'account', 'stock', 'payment'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/force_done_picking_wizard_view.xml',
        'views/invoice_stock_move_view.xml'

    ],
    'images': ['static/description/banner.png',
               'static/description/banner.png', ],

    'license': 'AGPL-3',
    'email': "support@banibro.com",
    'installable': True,
    'auto_install': False,
    'application': True,
}
