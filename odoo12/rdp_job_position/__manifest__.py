{
    'name': 'Job Position Extended',
    'version': '12.0.0.2',
    'category': 'Human Resources',
    'author': 'RDP',
    'summary': 'Managers Responsibility',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     Managers Responsibility
    """,
    'depends': ['base', 'hr'],
    'data': [
         # 'security/ir.model.access.csv',
         # 'data/data.xml',
         'views/job_position_extended.xml',
    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}