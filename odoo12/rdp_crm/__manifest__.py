{
    'name': 'CRM Inherited',
    'version': '12.0.1.0.0',

    'author': 'RDP',
    'company': 'rdp',
    'website': "https://rdp.in",
    'depends': ['base', 'mail', 'crm','crm_leads_buttons','sale'],
    'data': [
        'data/mail_template.xml',
        'views/crm_lead.xml',
    ],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
