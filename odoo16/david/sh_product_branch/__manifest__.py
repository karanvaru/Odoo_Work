# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

{
    "name": "Product Multiple Branch",

    "author": "Softhealer Technologies",

    "website": "https://www.softhealer.com",

    "version": "16.0.1",

    "license": "OPL-1",

    "support": "support@softhealer.com",

    "category": "Productivity",

    "summary": "Multiple Locations Multiple Branches Multiple Stores Multiple Chain Multiple Branch Management Multi Branch app Multiple Unit multiple Operating unit branch Sales Purchase branch Invoicing branch warehouse branch Product Branch branch app Odoo",

    "description": """"Product Multiple Branch" module is a base module for multi branch modules.""",

    "depends": ["product", "sh_base_branch"],

    "data": [
        "security/product_rules.xml",
        "views/product_views.xml",
    ],

    "images": ["static/description/background.png", ],
    "installable": True,
    "auto_install": False,
    "application": True,
    'uninstall_hook': 'uninstall_hook',
    "price": 5,
    "currency": "EUR"
}
