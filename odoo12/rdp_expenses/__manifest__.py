{
    'name': 'RDP Expenses',
    'version': '12.0.1.0.0',
    'author': 'RDP',
    'company': 'RDP',
    'website': "https://www.openhrms.com",
    'depends': ['base', 'hr', 'mail', 'hr_expense'],
    'data': [
        'security/security.xml',
        # 'security/ir.model.access.csv',
        'views/expenses.xml',
        'views/expenses_line_sheet.xml',

    ],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}