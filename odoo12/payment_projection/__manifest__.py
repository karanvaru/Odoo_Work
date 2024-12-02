{
    'name': "Payment Projection", 
    'version': '12.1.0.0',
    'author': 'RDP',
    'website': 'https://www.rdp.in',
    'summary': 'Payment Projection',
    'description': """
    It is about Payment Projection.
    """,
    'depends': ['base', 'mail','account','advance_payment','hr'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/payment_projection_sequence.xml',
        'views/effective_date.xml',
        'views/payment_projection.xml',
    ],
    'demo': [],
    'images': [],
    'license': 'OPL-1',
    'installable': 'True',
    # 'application': 'False',
    # 'auto_install': 'False',
}
# Developed By: Dayanithi T 