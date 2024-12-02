{
    'name': 'Ki Spv Costing Excel',
    'version': '16.0.0.0',
    'summary': 'Ki Spv Costing Excel',
    'author': 'Kiran Infosoft',
    'website': "http://www.kiraninfosoft.com",
    'license': 'OPL-1',
    'description': """Ki Spv Costing Excel""",
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        "views/sale_order_inherit_view.xml",
        "views/quote_excel_template_view.xml",
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
