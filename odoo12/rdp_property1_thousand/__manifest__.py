{
    'name': 'Property1 1000 App',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module help us to develop Global Feedback App ',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     property_one_app_action_view
    """,
    'depends': ['base', 'mail', 'purchase','amazon_ept','product','rdp_exit14'],
    'data': [

        'security/ir.model.access.csv',
        'views/property_one.xml',
        'views/purchase_order_view.xml',
        'data/data.xml',
        'views/fm_admin_view.xml',
    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}