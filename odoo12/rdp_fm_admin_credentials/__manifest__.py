{
    'name': 'FM Admin Credentials',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module is Used for storing of multiple Usernames and Passwords of Different Departments',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     This module help us to develop fm admin credentials'
    """,
    'depends': ['base','mail', 'crm','hr'],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'wizards/reset.xml',
        'wizards/credentials.xml',
        'views/admin_credentials.xml'


    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}