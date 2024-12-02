{
    'name': 'Vendor Registration Form',
    'version': '17.9.4',
    'author': 'RDP',
    'category': 'Uncategorized',
    'depends': ['base', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/vendor_registration.xml',
        'views/contacts_view_extend.xml',
        'views/existing_email_view.xml',
        'views/assests.xml',
    ],
    'qweb': [
        'static/src/css/vendor_registration.css',  # Include your template if it contains QWeb code
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {
        'web.assets_frontend': [
            'rdp_vendor_registration_form/static/src/css/vendor_registration.css',
        ],
    },
}
