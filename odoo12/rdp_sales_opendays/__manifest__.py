{
    'name': 'RDP Sales Opendays',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module help us to develop sales opendays',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     This module help us to develop sales opendays'
    """,
    'depends': ['base', 'rma'],
    'data': [
        'views/opendays_sales_view.xml'
    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}