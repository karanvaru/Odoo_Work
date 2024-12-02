{
    'name': 'Manufacturing Opendays',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module help us to develop manufacturing opendays',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     This module help us to develop manufacturing opendays
    """,
    'depends': ['mrp'],
    'data': [
        'views/manufacturing_view.xml',
        'views/work_order.xml',
            ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}