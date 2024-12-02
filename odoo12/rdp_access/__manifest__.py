{
    'name': 'CRM Inherited',
    'version': '12.0.1.0.0',

    'author': 'RDP',
    'company': 'rdp',
    'website': "https://rdp.in",
    'depends': ['base', 'mail', 'crm'],
    'data': [
        "security/security.xml",
        "security/ir.model.access.csv",
        'views/crm_lead.xml',
    ],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
