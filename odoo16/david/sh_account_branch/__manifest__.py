# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

{
    "name": "Account Multi Branch | Invoice Multi Branch",

    "author": "Softhealer Technologies",

    "website": "https://www.softhealer.com",

    "version": "16.0.1",

    "license": "OPL-1",

    "support": "support@softhealer.com",

    "category": "Accounting",

    "summary": "Invoice Multiple Locations Invoice Multiple Branches Multiple Stores Multiple Chain Multiple Branch Management Multi Branch Multiple Unit multiple Operating unit branch branch Invoicing branch Credit note branch Accounting Report Multi Branch Invoice Odoo Invoices Branch Invoice Branch Invoice Multi Locations Invoice Multi Store Invoice Multi Chain Multi Branch Management Multi Unit Setup Multi Unit Management Multi Unit Odoo Multiple Branch Odoo Multi Unit Features Invoices Multi Locations Invoices Multi Store Invoices Multi Chain Invoices Multi Unit Invoice Branch Report Invoice Stores Report Invoice Locations Report Invoice Unit Report Invoice Chains Report Multi Unit Invoices Multi Unit Invoice Invoice Branch Management Multi Branch Invoice Multi Branch Invoices Invoice Multi Branch Invoice Multiple Branch Multiple Branch Invoice Invoice Multi Unit Invoices Multi Branch Invoices Multiple Locations Multiple Branch Invoices Multi Branch Accounting Bill Multi Unit Bill Multiple Unit Bill Multiple Branch Invoicing Process Multi Branch Multi Unit Vendor Bills Multi Branch Credit Note Multi Branch Credit Note Debit Note Multi Branch Multi Branch debit Note Multi Branch Journal Entries Accounting Multi Branch",

    "description": """Odoo provides multiple company feature which helps to manage your different company in one odoo database. But if you want to manage your business with multiple locations/branches/Stores/Chains in one database so that feature is not available in the odoo. Our this app provides feature to manage your business with multi branches.""",

    "depends": ["account", "sh_base_branch", "sh_product_branch"],

    "data": [
        "security/account_rules.xml",
        "security/account_move_rules.xml",
        "security/account_payment_rules.xml",

        "views/account_move_views.xml",
        "views/account_tax_views.xml",
        "views/account_journal_views.xml",
        "views/account_payment_term_views.xml",
        "views/account_fiscal_position_views.xml",
        "views/account_payment_views.xml",

        "reports/invoice_report.xml",
    ],


    "images": ["static/description/background.png", ],
    "installable": True,
    "auto_install": False,
    "application": True,
    'uninstall_hook': 'uninstall_hook',
    "price": 35,
    "currency": "EUR"
}
