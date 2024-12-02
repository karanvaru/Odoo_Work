{
    'name': 'Charity Portal',
    'version': '17.0.2.8',
    'license': "OPL-1",
    'summary': '''Charity Portal''',
    'description': '''
        Charity Portal
    ''',
    'depends': [
        'base',
        'contacts',
        'website',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/vendor_send_mail.xml',
        'views/res_partner_view.xml',
        'views/vendor_verification_template.xml',
        'views/personality_profile_page_tempate.xml',
        'views/confidentailly_policy_page_template.xml',
        'views/verification_thanks_page_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'https://cdn.jsdelivr.net/npm/signature_pad@4.0.0/dist/signature_pad.umd.min.js',
            'de_charity_portal/static/src/js/add_children_button.js',
            'de_charity_portal/static/src/js/digital_signature.js',
        ],
    },

    'images': ['static/description/banner.gif'],
    'installable': True,
    'price': 75,
    'currency': 'EUR',
}
