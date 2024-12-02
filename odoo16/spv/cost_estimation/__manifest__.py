# -*- coding: utf-8 -*-
{
    'name': "Cost Estimation",

    'summary': """
    General Cost Estimation Module""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Digizilla",
    'website': "http://www.digizilla.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'crm',
    'version': '15.1',

    # any module necessary for this one to work correctly
    # account_budget
    'depends': ['sale_crm', 'project', 'stock', 'purchase', 'stock_account', 'sale_management'],

    # always loaded
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/settings.xml',
        'views/cost_estimation.xml',
        'views/crm.xml',
        'views/product.xml',
        'views/quotation.xml',
        # 'views/templates.xml',
        'views/project_task_view.xml',
        'views/project_project.xml',
        'views/account_journal_view.xml',
        'views/stock_picking_views.xml',
        'views/res_partner_views.xml',
        'wizard/set_markup_view.xml',
    ],
    'images': [
        'static/description/icon.png',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
