{
    'name': 'POS Session Report | POS Z Report | POS Session Z Report | Session Cash In Out',
    'description': """
     Using this module you can print POS Session Report or Z Report from frontend end Using Thermal Printer.
    """,    
    'version': '16.1.1.2',
    'sequence': 1,
    'email': 'apps@maisolutionsllc.com',
    'website':'http://maisolutionsllc.com/',
    'category': 'Point of Sale',
    'summary': 'Using this module you can print POS Session Report or Z Report from frontend end Using Thermal Printer.',
    'author': 'MAISOLUTIONSLLC',
    'price': 11,
    'currency': 'EUR',
    'license': 'OPL-1',    
    'depends': ['point_of_sale'],
    "data": [
        'views/pos_config_view.xml',
        'views/report_pos_session.xml',
    ],
    'images': ['static/description/main_screenshot.gif'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'assets': {
        'point_of_sale.assets': [
            'mai_pos_session_report_thermal/static/src/js/mai_session_report.js',
            'mai_pos_session_report_thermal/static/src/css/mai_session_report.css',
            'mai_pos_session_report_thermal/static/src/xml/mai_session_report.xml',
        ],
    },     
}
