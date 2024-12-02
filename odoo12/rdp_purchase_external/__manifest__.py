{
    'name': 'Open Days Purchase',
    'version': '12.0.1.0.0',
    'sequence': -140,
    'author': 'RDP',
    'company': 'rdp',
    'website': "https://www.openhrms.com",
    'depends': ['base', 'hr', 'mail', 'purchase', 'purchase_request','purchase_requisition', 'product', 'sh_po_tender_management',
                'payment_projection'],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase.xml',

    ],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
