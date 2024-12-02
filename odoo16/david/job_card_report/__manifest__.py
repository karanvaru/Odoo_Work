# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': "Job Card Reports",
    'version': '5.2.6',
    'price': 49.0,
    'currency': 'EUR',
    'category' : 'Services/Project',
    'license': 'Other proprietary',
    'summary': """Job Card Analysis Report""",
    'description': """
Job Card Report
job card bi report
Job Card Instructions Report
Job Card Costsheets Report
Job Card Requisitions Lines Report
Job Card Timesheets Report

""",
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "www.probuse.com",
    'support': 'contact@probuse.com',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/job_card_report/946',#'https://youtu.be/f-DNvSVAVqk',
    'images': ['static/description/jcar.jpg'],
    'depends': [
                'job_card', 
                ],
    'data':[
       'views/job_card_view.xml'
    ],
    'installable' : True,
    'application' : False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
