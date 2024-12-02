# -*- coding: utf-8 -*-
{
    'version': '1.2',
    'name': 'Asterisk PBX Queues',
    'summary': 'Queue management addon',
    'description': '',
    'author': 'Odooist',
    'price': 0,
    'currency': 'EUR',
    'maintainer': 'Odooist',
    'support': 'odooist@gmail.com',
    'license': 'OPL-1',
    'category': 'Phone',
    'depends': ['asterisk_base'],
    'data': [
        'security/admin_access_rules.xml',
        'security/agent_access_rules.xml',
        'security/agent_record_rules.xml',
        # Views
        'views/queues.xml',
        'views/user.xml',
        'views/settings.xml',
        # Data
        'data/base_queues_conf_templates.xml',
        'data/settings_templates.xml',
    ],
    'demo': [
        'demo/user.xml',
        'demo/queue.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
