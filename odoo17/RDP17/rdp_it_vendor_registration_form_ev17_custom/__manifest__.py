{
    'name': 'Vendor Registration Form',
    'version': '17.0.0.1',
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
            'rdp_it_vendor_registration_form_ev17_custom/static/src/css/vendor_registration.css',
        ],
    },
}
