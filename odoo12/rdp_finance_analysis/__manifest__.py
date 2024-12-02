{
    'name': 'RDP Finance Analysis',
    'version': '12.0.1.0.0',
    'sequence': 10,
    'author': 'RDP',
    'company': 'RDP Workstation',
    'website': "https://www.rdp.in",
    'description': """
     This module help us to track and analysis all the transactions'
    """,
    'depends': ['base','mail','account','rdp_account','rdp_payments','sale','hr_expense'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/account_payment.xml',
        'wizard/hr_expense_sheet_register_payment.xml',
        'views/hr_expense.xml',
        'views/hr_expense_sheet.xml',
        # 'views/account_invoice.xml',
        # 'views/hr_payslip.xml',
        'views/finance_analysis.xml',
        'views/finance_configuration.xml',
        # 'data/finance_analysis_reports.xml',
    ],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
# Dayanithi
