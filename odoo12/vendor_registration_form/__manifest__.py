# -*- coding: utf-8 -*-



{
    'name' : 'Vendor Registration Form',
    'version' : '1.0',
    'category': 'Operations/Purchase',
    'license': 'Other proprietary',
    'description': """
vendor registration form
supplier registration form
vendor register
register vendor
    """,
    'summary' : 'Website Vendor Registration Form',
    'author' : 'RDP',
    'website' : 'wwww.rdp.in',
    'depends' : [
        'contacts',
        'website',
        'product',
    ],

    'data' : [
        'data/mail_data.xml',
        'views/website_vendor_templates.xml',
        'views/res_partner_view.xml',
        'views/product_category_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
