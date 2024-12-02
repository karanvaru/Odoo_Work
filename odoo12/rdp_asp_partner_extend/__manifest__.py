# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'ASP Extend',
    'version': '12.0.0.5',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module help us to add SO in helpdesk. ',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     To send parts to field engineer
    """,
    'depends': ['base','helpdesk','asp_partner'],
    'data': [

        'security/ir.model.access.csv',
        'views/asp_partner.xml',
        'views/website_asp_templates.xml',
        # 'views/website_form.xml'

    ],

  
    'installable': True,


}
