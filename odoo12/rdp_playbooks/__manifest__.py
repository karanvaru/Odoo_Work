    #Developed by RDP-Dayanithi
{
    'name': 'RDP PlayBooks',
    'version': '12.0.0.0',
    'author': 'RDP',
    'company': 'RDP',
    'website': 'http://www.rdp.in',
    'category': 'Accounting',
    'summary': 'Playbooks ',
    'description': """ RDP PlayBooks """,
    'depends': ['base','mail'],
    'data': [
        'security/ir.model.access.csv',
        # 'security/security.xml',
        'data/data.xml',
        'views/playbooks.xml',
        'views/workflows.xml',
    ],
    # 'images': [''],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
