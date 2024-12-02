{
    'name': 'RDP Inventory',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'In this module added fields to the existed module ',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     To send parts to field engineer
    """,
    'depends': ['base','stock'],
    'data': [


        'views/stock_inherit.xml',


    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}