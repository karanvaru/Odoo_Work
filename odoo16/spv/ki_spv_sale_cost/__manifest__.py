{
    'name': 'Ki SPV Sale Cost',
    'version': '16.0.0.0',
    'summary': 'Ki Spv Sale Costing',
    'author': 'Kiran Infosoft',
    'website': "http://www.kiraninfosoft.com",
    'license': 'OPL-1',
    'description': """Ki Spv Sale Costing""",
    'depends': ['sale_project', 'base', 'sale_stock'],
    'data': [
        "security/ir.model.access.csv",
        "views/sale_order_inherit_view.xml",
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
