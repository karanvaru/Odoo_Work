{
    'name': "Monday 2 Monday Dashboard",
    'version': '12.0.0.1',
    'author': 'RDP',
    'website': 'https://www.rdp.in',
    'summary': 'Monday 2 Monday Dashboard',
    'description': """
    It is about Monday 2 Monday Dashboard.
    """,
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/m2m_dashboard_sequence.xml',
        'views/m2m_dashboard.xml',
        
    ],
    'demo': [],
    'images': [],
    'license': 'OPL-1',
    'installable': 'True',
    'application': 'True',
    # 'auto_install': 'False',
}
