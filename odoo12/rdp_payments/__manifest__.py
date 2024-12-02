{
    'name': 'RDP Payment Customization',
    'version': '1.0',
    'summary': 'Payment screen customization according to RDP requirements.',
    'description': 'Payment screen customization according to RDP requirements.',
    'category': 'account',
    'author': 'SunArc Technologies',
    'website': 'www.sunarctechnologies.com',
    'license': 'AGPL-3',
    'depends': ['account','rdp_account'],
    'data': [
        'data/account_jr.xml',
        'views/payment.xml'],
    'installable': True,
    'auto_install': False,
}
