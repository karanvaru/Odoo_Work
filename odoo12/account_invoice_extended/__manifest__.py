{
    'name': 'RDP Account Invoice Extended',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module is used to add the  new fields in account.invoice module',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     'This module is used to add the  new fields in account.invoice module',
    """,
    'depends': ['account','ki_accounting_reports','mail'],
    'data': [
         'views/account_invoice_extended_views.xml',
         'security/ir.model.access.csv',
         'views/account_invoice_line_view.xml',
         'views/account_account_view.xml',
         'views/account_move.xml',
        #  'views/attachment_view.xml',
         'views/account_move_line.xml',
    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}