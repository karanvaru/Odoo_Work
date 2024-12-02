{
    'name': 'Kumbhasthalam App',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module help us to develop Kumbhasthalam App ',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     Kumbhasthalam App
    """,
    'depends': ['base', 'mail'],
    'data': [

        'security/ir.model.access.csv',
        'data/data.xml',
        'views/kumbhasthalam.xml'
    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}