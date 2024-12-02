{
    'name': 'Gate Pass',
    'version': '3.1',
    'category': 'Inventory',
    'author': 'RDP',
    'summary': 'This module used to create a Gate pass',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     This module used to gate pass for outwards screen'
    """,
    'depends': ['base', 'hr', 'mail', 'product', 'stock'],
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/gate_pass.xml',
        'views/stock.xml',
        'report/gatepass_template.xml',
        'report/report.xml',
    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}