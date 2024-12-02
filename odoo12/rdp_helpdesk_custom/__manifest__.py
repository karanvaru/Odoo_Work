# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'RDP Helpdesk Custom',
    'version': '12.0.1.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'RDP Helpdesk Customizations ',
    'website': 'www.rdp.in',
    'sequence': '10',

    'depends': ['base', 'helpdesk', 'rdp_tat','rdp_helpdesk_so'],
    'data': [

        'security/ir.model.access.csv',
        'views/helpdesk_custom_view.xml',
        'views/helpdesk_stage.xml',
        'data/cron.xml',
        'data/back_order_template.xml',
        'data/psr_stage_template.xml',
        'data/customer_side_pending_stage.xml',
        'data/back_order_stage_custom_cron.xml',
        'data/customer_side_pending_stage_custom_cron.xml',
        'data/PSR_opened_stage_custom_cron.xml',
    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}
