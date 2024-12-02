{
    'name': 'Ki Spv Costing',

    'version': '16.0.0.2',

    'summary': 'Ki Spv Costing',

    'author': 'Kiran Infosoft',

    'website': "http://www.kiraninfosoft.com",

    'license': 'OPL-1',

    'description': """Ki Spv Costing""",

    'depends': ['crm', 'contacts', 'base', 'product'],

    'data': [
        "security/ir.model.access.csv",
        "data/crm_costing_sheet_sequence.xml",
        "views/cost_sheet_template_view.xml",
        "views/crm_inherit_view.xml",
        "views/crm_cost_sheet_view.xml",
        "views/product_product_inherit_view.xml",
        "views/res_partner_inherit_view.xml",
        "wizard/cost_sheet_template_wizard_view.xml",
    ],

    'installable': True,

    'application': False,

    'auto_install': False,
}
