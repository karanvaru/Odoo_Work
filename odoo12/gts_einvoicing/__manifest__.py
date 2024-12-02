# -*- encoding: utf-8 -*-

{
    'name': 'GST E-Invoicing',
    'version': '21.0.0.3',
    'category': 'Integration',
    'description': """
        Module to allow E-Invoicing integration with Taxpro
        Documentation
        https://help.taxprogsp.co.in/ewb/authentication_url___method_get_.htm?ms=AgI%3D&st=MA%3D%3D&sct=MA%3D%3D&mw=MjQw&ms=AgI%3D&st=MA%3D%3D&sct=MA%3D%3D&mw=MjQw
    """,
    'author': 'Geo Technosoft',
    'sequence': 1,
    'website': 'https://www.geotechnosoft.com',
    'depends': ['account', 'stock', 'web_notify', ],
    'data': [
        'security/ir.model.access.csv',
        'security/e_invoice_group.xml',
        'reports/invoice_report.xml',
        'data/uom_data.xml',
	    'data/res_country_state_data.xml',
        'data/uom_data.xml',
        'wizard/cancel_einvoice.xml',
        'wizard/cancel_eway.xml',
        'views/einvoicing_configuration.xml',
        'views/account_invoice.xml',
        'views/stock_warehouse.xml',
    ],
    'application': True,
    'installable': True,
}
