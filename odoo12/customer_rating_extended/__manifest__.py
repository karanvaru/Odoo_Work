{
    'name': 'RDP Customer Rating Extended',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP ',
    'summary': 'This module help us to develop Customer Rating',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     This module help us to develop Customer Rating
    """,
    'depends': ['base', 'rating', 'helpdesk'],
    'data': [
         'views/customer_rating_view.xml',
    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}