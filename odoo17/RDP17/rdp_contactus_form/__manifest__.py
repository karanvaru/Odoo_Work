{
    'name': 'RDP Contactus Form',
    'version': '17.0.0.2',
    'license': "OPL-1",
    'category': 'helpdesk',
    'author': 'Kiran Infosoft.',
    'website': "http://www.kiraninfosoft.com",

    'depends': ['base','product', 'helpdesk', 'website','base_address_extended'],
    'data': [
        # 'views/contact_us_from.xml',
        'data/ir_sequence_data.xml',
        'views/contact_use_template.xml',
        'views/helpdesk_ticket.xml',
        'views/res_config_setting_view.xml',
        'views/thankyou_ticket.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'rdp_contactus_form/static/scss/contact_form_page.scss',
        ],
    },
    'installable': True,
}
