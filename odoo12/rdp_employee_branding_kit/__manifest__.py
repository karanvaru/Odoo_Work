{
    'name': 'Employee Branding Kit',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': "In this module the different type of checklists are  given to the different departments of employees " ,
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     In this module the different type of checklists are  given to the different departments of employees
    """,
    'depends': ['base', 'mail', 'hr'],
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/branding_kit.xml',
        'views/employee_page_branding_kit.xml',


    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,
}
