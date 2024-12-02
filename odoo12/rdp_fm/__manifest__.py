{
    'name': 'RDP FM',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module help us to develop 4Form Tickets',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     This module help us to develop Hr Tickets'
    """,
    'depends': ['base', 'hr'],
    'data': [
         'security/ir.model.access.csv',
         'data/data.xml',
         'views/f_m_view.xml',
    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}