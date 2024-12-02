{
    'name': 'Application Checklist',
    'version': '12.0.1.0.0',
    'summary': """Manages Application Check List Process""",
    'description': """This module is used to Employee Application CheckList progress.""",
    'category': 'Human Resources',
    'author': 'RDP',
    'company': 'RDP',
    'website': "https://www.rdp.in",
    'depends': ['base', 'mail','hr','hr_recruitment'],
    'data': [
        'views/application_form_inherit_view.xml',
        'views/app_checklist_view.xml',
    ],
    'demo': [],
    # 'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

