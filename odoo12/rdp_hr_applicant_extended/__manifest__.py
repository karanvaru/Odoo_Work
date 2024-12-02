{
    'name': 'HR Applicant Extended',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module help is used add new fields, templates in the existed module',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     Test App
    """,
    'depends': ['base', 'mail', 'hr_recruitment'],
    'data': [

        'report/reports.xml',
        'data/mass_email_candidates.xml',


    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}
