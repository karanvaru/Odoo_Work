# -*- coding: utf-8 -*-

{
    'name': "RDP IT All Apps Relation Field 1 Ev12 Custom",
    'summary': """RDP IT All Apps Relation Field 1 Ev12 Custom""",
    'description': """RDP IT All Apps Relation Field 1 Ev12 Custom""",
    'author': "RDP",
    'website': "www.rdp.in",
    'version': '12.0.1',
    'depends': [
        'purchase_stock',
        'account',
        'sale_stock','mrp'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_order.xml',
        'views/account_move.xml',
        'views/sale_order.xml',
        'views/stock_picking.xml',
        'views/account_move_line.xml',
        'views/mrp_production.xml',
        'views/stock_scrap.xml',
        'views/stock_move.xml',
        'views/stock_inventory.xml'
    ],
    "application": True,
    'installable': True,
}
