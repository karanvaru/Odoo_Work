# -*- coding: utf-8 -*-
{
    'name': "RDP Website Snippet",
    'version': '12.0',
    'license': 'OPL-1' ,
    'summary': """RDP Website Snippet""",
    'author': "RDP",
    'website': "http://www.rdp.in",
    'sequence': 1,
    'category': 'website',
    'depends': ['website_blog','web','website'],
    'data': [
        'views/slider_template.xml',
        'views/trusted_image_slider.xml',
        'views/website_blog_slider_snippet.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
