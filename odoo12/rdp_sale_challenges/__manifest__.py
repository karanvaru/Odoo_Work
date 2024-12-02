{
    'name': 'Sales Challenges',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module help us to develop sales requirements',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     This module help us to develop sales requirements'
    """,
    'depends': ['sale','base','mail','sales_team'],
    'data': [
        # 'security/sale_challenges_security.xml',
        'security/ir.model.access.csv',
        'wizards/sale_response.xml',
        'views/sale_challenge_view.xml',
        'data/data.xml',
        'data/mail_template.xml',
        'data/create_sc_template.xml',
        'data/status_wise_mail_template.xml'


    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}