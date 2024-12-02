# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

{
    "name": "Base Multiple Branch",

    "author": "Softhealer Technologies",

    "website": "https://www.softhealer.com",

    "version": "16.0.1",

    "license": "OPL-1",

    "support": "support@softhealer.com",

    "category": "Extra Tools",

    "summary": "Inventory Multiple Locations Warehouse Multiple Branches Multiple Stores Multiple Chain Multiple Branch Management Multi Branch Multiple Unit multiple Operating unit branch Report Sale Multiple Branch Purchase Multiple Branches base branch Odoo",

    "description": """Odoo provides multiple company feature which helps to manage your different company in one odoo database. But if you want to manage your business with multiple locations/branches/Stores/Chains in one database so that feature is not available in the odoo. Our this app provides feature to manage your business with multi branches.""",

    "depends": ["base_setup","mail"],

    "data": [
        "security/res_branch_groups.xml",
        "security/res_branch_rules.xml",
        "security/res_partner_rules.xml",
        "security/ir.model.access.csv",
        "views/res_branch_views.xml",
        "views/res_partner_views.xml",
        "views/res_users_views.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'sh_base_branch/static/src/js/switch_branch_menu/switch_branch_menu.js',
            'sh_base_branch/static/src/js/BranchService.js',
            'sh_base_branch/static/src/js/switch_branch_menu/switch_branch_menu.xml',
        ],
    },
    "images": ["static/description/background.png", ],
    "installable": True,
    "auto_install": False,
    "application": True,
    'uninstall_hook': 'uninstall_hook',
    "price": 5,
    "currency": "EUR"
}
