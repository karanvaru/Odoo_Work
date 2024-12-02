# Developed by Dayanithi
{
    'name': 'RDP HR Payroll Reports',
    'version': '12.0.0.0',
    'category': 'HR',
    'author': 'RDP',
    'summary': 'This module used to Generate Payroll Excel Report',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     This module used to Generate Excel Report'
    """,
    'depends': ['base', 'hr', 'l10n_in_hr_payroll','report_xlsx'],
    'data': [
        # 'data/sequence.xml',
        # 'security/ir.model.access.csv',
        # 'views/stock.xml',
        # 'report/gatepass_template.xml',
        'reports/report.xml',
    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}