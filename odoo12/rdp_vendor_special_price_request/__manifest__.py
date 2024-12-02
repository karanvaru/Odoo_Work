{
    'name': 'CRM Vendor Special Price Request',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module help us to develop Vendor Special Price Request',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     This module help us to develop Vendor Special Price Request
    """,
    'depends': ['base', 'crm', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/vendor_special_price_view.xml',

    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}