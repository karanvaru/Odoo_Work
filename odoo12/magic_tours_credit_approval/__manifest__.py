# -*- encoding: utf-8 -*-

{
    'name': 'Magic Tour Credit Approval',
    'category': 'Contact',
    'version': '16.0',
    'description': "Magic Tour Credit Approval",
    'installable': True,
    'depends': ['base','mail','contacts','website','portal'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/credit_approval_view.xml',
        'views/webform_template.xml',
        'views/credit_portal_template.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}