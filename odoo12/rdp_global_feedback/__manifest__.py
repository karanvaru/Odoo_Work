{
    'name': 'Global Feedback App',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module help us to develop Global Feedback App ',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
    Global Feedback App
    """,
    'depends': ['base', 'mail','website'],
    'data': [

        'security/ir.model.access.csv',
        'views/feedback.xml',
        'views/global_feedback_portal.xml',
        'data/data.xml',
        'data/ir_model_data.xml',
    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}