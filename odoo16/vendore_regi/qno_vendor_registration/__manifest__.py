{
    'name': 'Vendor Registration',
    'summary': """ Vendor Registration """,
    'version': '17.0.0.0.2',
    'category': 'Extra Tools',
    "website": "http://www.qnomix.com/",
    'description': """  Vendor Registration  """,
    'author': 'Qnomix',
    'license': 'LGPL-3',
    'depends': ['base', 'account', 'contacts', 'website', 'l10n_in', 'base_address_extended'],
    'data': [
        'security/ir.model.access.csv',
        'data/vendor_send_mail.xml',
        'data/data_organization_type.xml',
        'wizards/odoo_sap_master_update_view.xml',
        'views/res_partner_view.xml',
        'views/organization_type_view.xml',
        'views/business_category_view.xml',
        'views/vendor_registration_template.xml',
        # 'views/sap_configuration_view.xml',
        'views/res_company_view.xml',
        'views/customer_vendor_group_view.xml',
        'views/res_users_view.xml',
        'views/res_config_settings_view.xml',
        'views/account_payment_term_view.xml',

        'views/menu_item.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'qno_vendor_registration/static/src/js/vendore_primary_details_validation.js',
        ],
    },

    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
