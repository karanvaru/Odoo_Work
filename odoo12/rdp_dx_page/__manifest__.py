{
    'name': 'RDP Dx Page',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module help us to develop RDP Dx Page',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     This module help us to develop RDP Dx Page'
    """,
    'depends': ['base', 'mail', 'dx_rdp', 'five_why'],
    'data': [
          'security/ir.model.access.csv',
          'wizards/dx_cancel_view.xml',
          'views/rdp_dx_view.xml',
          'views/check_list.xml',
    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}