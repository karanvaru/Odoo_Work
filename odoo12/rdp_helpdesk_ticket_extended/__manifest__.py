{
    'name': "Helpdesk Extended",
    'version': '12.0.0.1',
    'author': 'RDP',
    'website': 'https://www.rdp.in',
    'summary': 'Helpdesk Extended',
    'description': """
    Helpdesk Extended
    """,
    'depends': ['base', 'helpdesk'],
    'data': [
        'security/ir.model.access.csv',
        'views/helpdesk_ticket_extended.xml',

    ],
    'demo': [],
    'images': [],
    'license': 'OPL-1',
    'installable': 'True',
    # 'application': 'False',
    # 'auto_install': 'False',
}
