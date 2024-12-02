{
    'name': 'RDP Contactus Form',
    'version': '17.0.0.1',
    'license': "OPL-1",
    'category': 'helpdesk',
    'author': 'RDP.',
    'website': "http://www.rdp.in",

    'depends': ['base','product', 'stock','helpdesk', 'website','base_address_extended','rdp_it_custom_module_ev17_custom'],
    'data': [
        # 'views/contact_us_from.xml',
        'security/security.xml',
        'data/ir_sequence_data.xml',
        'views/contact_use_template.xml',
        'views/helpdesk_ticket.xml',
        'views/res_config_setting_view.xml',
        'views/thankyou_ticket.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'rdp_it_contactus_form_ev17_custom/static/scss/contact_form_page.scss',
            'rdp_it_contactus_form_ev17_custom/static/src/js/contact_us_template.js'
        ],
    },
    'installable': True,
}
