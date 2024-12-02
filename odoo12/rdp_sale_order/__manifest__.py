{
    'name': 'RDP Sale Order Inherit',
    'version': '12.0.0.0.1',
    'sequence': 10,
    'author': 'RDP',
    'company': 'RDP',
    'website': "https://www.rdp.in",
    'depends': ['base','mail','sale','contacts','sale_stock','sale_management','bi_rma','sale_margin','sale_margin_percent','stock','rdp_gatepass','product'],
    'data': [
        # 'security/security.xml',
        'security/ir.model.access.csv',
        # 'data/sequence.xml',
        'views/sale_order.xml',
        'views/stock_picking.xml',
        'views/sales_extended.xml',
        'views/res_partner.xml',
        'views/manufacturing.xml',
        'views/account_invoice.xml',
        'views/purchase_agreement.xml',
        'views/purchase_order.xml'
    ],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
