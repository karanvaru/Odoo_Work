{
    'name': 'RDP EBITDA Report',
    'version': '12.0.0.1',
    'category': 'Accounting',
    'author': 'RDP',
    'summary': 'This module Financial report EBITDA',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     This module help us to see EBITDA Reports in Accounting'
    """,
    'depends': ['base', 'account', 'account_reports'],
    'data': [

          'data/client_action_ebitda.xml',

    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}