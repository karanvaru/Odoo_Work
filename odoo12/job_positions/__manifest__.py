{
    'name': "Job Openings",
    'version': '12.0.0.1',
    'author': 'RDP',
    'website': 'https://www.rdp.in',
    'summary': 'Job Positions',
    'description': """
    It is about Job Positions.
    """,
    'depends': ['base', 'mail','hr'],
    'data': [
        'views/job_positions.xml',
        'views/job_positions_sequence.xml',
    ],
    'demo': [],
    'images': [],
    'license': 'OPL-1',
    'installable': 'True',
    # 'application': 'False',
    # 'auto_install': 'False',
}
