# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

{
    "name": "Point Of Sale Multi Branch | Point Of Sale Multiple Branch | POS Multiple Branch | POS Multi Branch",

    "author": "Softhealer Technologies",

    "website": "https://www.softhealer.com",

    "version": "16.0.1",

    "license": "OPL-1",

    "support": "support@softhealer.com",

    "category": "Point Of Sale",

    "summary": "POS Order Multiple Branch POS Locations POS Order Multi Branches Multiple Stores Multiple Chain Multiple Branch Management POS Branch Multiple Unit multiple Operating unit branch Point Of Sale branch Report Customer Branch Management Point Of Sale Orders Multi Branch Point Of Sale Order Multi Branch Odoo",

    "description": """Odoo provides multiple company feature which helps to manage your different company in one odoo database. But if you want to manage your business with multiple locations/branches/Stores/Chains in one database so that feature is not available in the odoo. Our this app provides feature to manage your business with multi branches.""",

    "depends": ["point_of_sale", "sh_base_branch","sh_account_branch","sh_stock_branch","sh_product_branch"],

    "data": [
        "security/base_security.xml",
        "views/pos_category_views.xml",
        "views/pos_config_views.xml",
        "views/pos_order_views.xml",
        "views/pos_payment_method_views.xml",
        "views/pos_payment_views.xml",
        "views/pos_session_views.xml",
        "views/report_pos_order_views.xml",
        "views/res_config_settings_views.xml",
    ],

    'assets': {
        'point_of_sale.assets': [
            'sh_pos_multi_branch/static/src/js/**/*.js',
            'sh_pos_multi_branch/static/src/xml/**/*.xml',
        ],
    },
    
    "images": ["static/description/background.png", ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "price": 0,
    "currency": "EUR"
}
