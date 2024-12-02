{
    'name': 'RDP inventory',
    'version': '12.0.1.0.0',
    'sequence': -160,
    'author': 'RDP',
    'company': 'rdp',
    'website': "https://www.openhrms.com",
    'depends': ['base', 'hr', 'mail','stock_landed_costs','sale','stock','stock_picking_batch','stock_cycle_count','sync_rma'],
    'data': [
        'security/ir.model.access.csv',
        'view/operations.xml',
        'view/stock_move_line.xml',
        # 'views/menus.xml',



    ],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
