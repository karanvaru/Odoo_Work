{
    'name': 'Job Position Extended',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'Creating the text field under the Career Path',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     Creating the text field under the Career Path'
    """,
    'depends': ['base', 'mail','hr'],
    'data': [
            'views/job_position.xml'
    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,
}
