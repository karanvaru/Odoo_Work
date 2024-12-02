# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Job Card Portal for Customer',
    'version' : '1.1.1',
    'price': 79.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': 'Job Card Portal on Website My Account',
    'description': """
       This app allows your customer to view their job card details on the portal of your website and do a signature on the portal on the job card form.
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'category': 'Services/Project',
    'images': ['static/description/card_image.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/job_card_portal_odoo/1343',
    'depends' : [
        'portal', 
        'job_card' 
    ],
    'data': [
        'views/portal_view.xml',
        'views/project_task_view.xml',
        'views/report_jobcard.xml'
    ],
   
    'installable': True,
    'application': False,
    'auto_install': False,
    
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
