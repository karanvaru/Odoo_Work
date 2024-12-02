{
    'name': 'HR Portal Extended',
    'version': '12.0.0.2',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module help is used add new fields, templates in the existed module',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     Test App
    """,
    'depends': ['base', 'mail', 'hr_recruitment', 'website_hr_recruitment'],
    'data': [

        'views/hr_applicant_view.xml',


    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}
