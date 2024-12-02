# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

{
    'name': "Add Portal Attachment",
    'summary': """Add Multiple Attachment from Portal Chatter""",
    'description': """Add Multiple Attachment from Portal Chatter""",
    'version': "0.1",
    'category': "Portal",
    'author': "Kiran Infosoft",
    'website': "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    'depends': [
        'website', 'website_mail', 'portal'
    ],
    'data': [
        'views/assets.xml'
    ],
    'qweb': ['static/src/xml/*.xml'],
    'auto_install': True,
}
