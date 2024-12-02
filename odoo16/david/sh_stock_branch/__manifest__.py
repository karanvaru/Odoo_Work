# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

{
    "name": "Inventory Multi Branch | Warehouse Multi Branch | Stock Multiple Branch | Inventory Multiple Branch",

    "author": "Softhealer Technologies",

    "website": "https://www.softhealer.com",

    "version": "16.0.1",

    "license": "OPL-1",

    "support": "support@softhealer.com",

    "category": "Warehouse",

    "summary": "Inventory Multiple Locations Warehouse Multiple Branches Multiple Stores Multiple Chain Multiple Branch Management Multi Branch Multiple Unit multiple Operating unit branch Internal Transfer branch Report Delivery Order Branch Management Inventory Branch Stock Branch Warehouse Branch Odoo Stock Branch Multi Branch Management Multi Unit Setup Multi Unit Management Multi Unit Odoo Multiple Branch Odoo Stock Multi Branch Stock Branch Report Stock Stores Report Delivery Order Branch Management Stock Branch Management Stock Multiple Locations Stock Multi Locations Stock Multi Store Stock Multi Chain Stock Multi Unit Multi Branch Stock Stock Multiple Branch Multiple Branch Stock Inventory Multiple Unit Stock Locations Report Stock Unit Report Stock Chains Report Inventory Multiple Locations Warehouse Multiple Branches Multi Unit Stocks Multi Unit Stock Inventory Branch Internal Transfer branch Report Inventory Multi Unit Multi Unit Features",

    "description": """Odoo provides multiple company feature which helps to manage your different company in one odoo database. But if you want to manage your business with multiple locations/branches/Stores/Chains in one database so that feature is not available in the odoo. Our this app provides feature to manage your business with multi branches.""",


    "depends": ["stock_account", "sh_base_branch", "sh_product_branch"],

    "data": [
        "security/stock_location_rules.xml",
        "security/stock_move_rules.xml",
        "security/stock_picking_rules.xml",
        "security/stock_quant_rules.xml",
        "security/stock_scrap_rules.xml",
        "security/stock_valuation_layer_rules.xml",
        "security/stock_warehouse_rules.xml",

        "views/stock_location_views.xml",
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml",
        "views/stock_quant_views.xml",
        "views/stock_scrap_views.xml",
        "views/stock_valuation_layer_views.xml",
        "views/stock_warehouse_views.xml",

        "reports/stock_report.xml",
    ],


    "images": ["static/description/background.png", ],
    "installable": True,
    "auto_install": False,
    "application": True,
    'uninstall_hook': 'uninstall_hook',
    "price": 35,
    "currency": "EUR"
}
