{
    'name': 'Inherit Model',
    'version': '17.0.0.1',
    'author': 'RDP',
    'category': 'Customizations',
    'depends': ['base', 'mail',
                'stock',
                'stock_account',
                'purchase_stock',
                'account',
                'sale_stock', 'mrp',
                'rdp_it_custom_module_ev17_custom',
                ],
    'data': [
        'views/purchase_order.xml',
        'views/account_move.xml',
        'views/sale_order.xml',
        'views/stock_picking.xml',
        'views/account_payment.xml',
        'views/account_move_line.xml',
        'views/mrp_production.xml',
        'views/stock_scrap.xml',
        'views/stock_move.xml',
        'views/stock_quant.xml',
        'views/res_partner.xml'

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
