{
    'name': 'RDP Contacts Inherited',
    'version': '12.0.0.0',
    # 'sequence': 100,
    'author': 'RDP',
    'company': 'rdp',
    'website': "https://www.rdp.in",

    'depends': ['base', 'contacts'],
    'data': [
         'security/ir.model.access.csv',
         'security/security.xml',
         'views/contacts_inherited.xml',
         'views/working_brands.xml',
    ],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
