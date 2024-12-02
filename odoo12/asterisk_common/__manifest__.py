{
    'name': "Asterisk Common (connector)",
    'version': '1.10',
    'price': 0,
    'currency': 'EUR',
    'author': "Odooist",
    'category': 'Phone',
    'license': 'OPL-1',
    'summary': 'Click2dial, set callerid name and more...',
    'description': 'Common module for other Asterisk addons',
    'depends': ['contacts'],
    'external_dependencies': {'python': ['phonenumbers']},
    'data': [
        # User's Data first!
        'data/user.xml',
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/admin_access_rules.xml',
        'security/admin_record_rules.xml',
        'security/agent_access_rules.xml',
        'security/user_access_rules.xml',
        'security/user_record_rules.xml',
        'views/menus.xml',
        'views/agent.xml',
        'views/agent_state.xml',
        'views/assets.xml',
        'views/ir_cron.xml',
        'views/res_partner.xml',
        'views/res_users.xml',
        'views/user.xml',
        'views/settings.xml',
        'views/about.xml',
        # Put it after settings as it goes under Settings menu.
        'views/event.xml',
        'views/user_settings.xml',
        # Wizards
        'wizards/user.xml',
        # Data
        'data/common_events.xml',
    ],
    'demo': [
        'demo/user.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    "qweb": ['static/src/xml/*.xml'],
    'images': [
        'static/description/partner.png',
        'static/description/agent-ping-stats.gif',
        'static/description/agent-events.png',
        'static/description/common-settings.png',
    ],
}
