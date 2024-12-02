{
    'name': 'BOE Settlement',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': "Bill of Exchange Submit",
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     Bill of Exchange Submit
    """,
    'depends': ['base', 'mail', 'account'],
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/boe_settlement.xml',
        'views/boe_smart_button.xml',
    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,
}
