{
    'name': "Employee Disciplinary",
    'version': '1.1',
    'author': 'Kanak Infosystems LLP.',
    'website': 'https://kanakinfosystems.com',
    'summary': 'Module used to raise a disciplinary against an employee, create a PIP(performance improvement plan) at the same time allows employee to raise an appeal',
    'description': """
    It is about employee disciplinary.
    """,
    'depends': ['base', 'mail', 'hr'],
    'data': [
        'security/security.xml',
        'views/disciplinary.xml',
        'views/mail.xml',
        'security/ir.model.access.csv',
        'data/disciplinary_data.xml',
    ],
    'demo': [],
    'images': [],
    'license': 'OPL-1',
    'price': 80,
    'currency': 'EUR',
    'installable': 'True',
    'application': 'False',
    'auto_install': 'False',
    'images': ['static/description/main_image.png'],
    'price': 60,
    'currency': 'EUR',
}
