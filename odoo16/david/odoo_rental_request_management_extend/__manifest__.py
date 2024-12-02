{
    'name': "Product Rental Request Management Extend",
    'version': '8.1.2',
    'summary': """Product Rental Request Management Extend.""",
    'description': """Product Rental Request Management Extend""",
    'license': 'Other proprietary',
    'category' : 'Website/Sale',
    'depends': [
        'account',
        'odoo_rental_request_management',
        'ki_invoice_extensions',
    ],

    'data':[
        'reports/invoice_report_template_view.xml',
        'views/account_move_line_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

