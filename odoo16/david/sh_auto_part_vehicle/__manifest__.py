# Part of Softhealer Technologies.
{
    "name": "All In One Auto Parts Management - Advance",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Industries",
    "summary": "Auto Parts Vehicle Management Auto Parts Attributes OEM Original Equipment Manufacture Fleet Repair Vehicle Repair Maintenance Fleet Service Repair Automotive Make Model Year Type Grade Engine Transmission Brand Equipment Maintenance Repair Operation Assets Maintenance Equipment Repair Maintenance Request Auto Parts Repair Auto Parts Maintenance Machine Maintenance Machine Repair Product Repair Assets Repair Car Repair Maintenance Product Maintenance Odoo",
    "description": """In automobile shops have numerous auto parts there is no count for parts and it's variants that's the way it is quite difficult to manage into the shop. So that's why we created a model that will help you to manage it. This module will help to manage an auto part by make, model, year, type, grade, engine, transmission, brand, product type & countries. You can also assign vehicles in auto parts product variants so it will become very easy to find the product using vehicle details. In this module provide two groups for user and manager so you can easily apply access rights for user and manager.""",
    "version": "16.0.1",
    "depends": [
        "website_sale",
        "website_sale_wishlist",
        "website_sale_comparison",
        "sale_management",
        "portal",
        "stock",
    ],
    "application": True,
    "data": [
        "security/motorcycle_security.xml",
        "security/ir.model.access.csv",
        "data/website_sale_data.xml",
        "views/sh_vehicle_motorcycle_views.xml",
        "views/sh_vehicle_type_views.xml",
        "views/sh_vehicle_make_views.xml",
        "views/sh_vehicle_mmodel_views.xml",
        "views/sh_vehicle_year_views.xml",
        "views/product_views.xml",
        "views/sh_vehicle_garde_views.xml",
        "views/sh_vehicle_engine_views.xml",
        "views/sh_vehicle_transmission_views.xml",
        "views/sh_vehicle_brand_views.xml",
        "views/sh_vehicle_product_type_views.xml",

        "views/sh_vehicle_snippet_templates.xml",

        "views/res_config_settings_views.xml",
        "views/website_sale_templates.xml",
        "views/sh_vehicle_table_templates.xml",
        "views/website_shop_attr_templates.xml",
        "views/sh_vehicle_garage_portal_templates.xml",
    ],

    'assets': {
        'web.assets_frontend': [
            'sh_auto_part_vehicle/static/src/js/search_new.js',
            'sh_auto_part_vehicle/static/src/js/snippets.js',
            'sh_auto_part_vehicle/static/src/js/custom.js',
            'sh_auto_part_vehicle/static/src/js/wishlist.js',
            'sh_auto_part_vehicle/static/src/js/add_to_cart.js',

            'sh_auto_part_vehicle/static/src/scss/custom.scss',
            'sh_auto_part_vehicle/static/src/css/snippets.css',
            'sh_auto_part_vehicle/static/src/scss/snippets.scss',
            "sh_auto_part_vehicle/static/src/xml/compitible_products.xml",
        ],
        'website.assets_wysiwyg': [
            'sh_auto_part_vehicle/static/src/js/editor.js',
        ],
    },
    "auto_install": False,
    "installable": True,
    "images": ["static/description/background.png", ],
    "license": "OPL-1",
    "price": 500,
    "currency": "EUR"
}
