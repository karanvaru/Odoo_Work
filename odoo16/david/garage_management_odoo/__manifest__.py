# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': "Garage Management System with Job Card",
    'version': '1.1.1',
    'depends': ['job_card', 'job_card_report', 'job_card_portal_odoo'],
    'category' : 'Services/Project',
    'price': 99.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Garage Management Odoo App with Job Card / Estimation / Requisition / Vehicle Details / Timesheets / Checklist / Instructions""",
    'description': """
    This app allows the garage manager (project manager) and project users (garage user) to manage the garage using a job card with vehicle details, cost sheet, timesheet, checklist, instruction, invoicing etc as shown in below screenshots.
""",
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "www.probuse.com",
    'support': 'contact@probuse.com',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/garage_management_odoo/1345',
    'images': ['static/description/gar_image.jpg'],    

    'data':[
        'security/ir.model.access.csv',
        'views/repair_category.xml',
        'views/vehicle_type.xml',
        'views/job_card_view.xml',
        'views/report_jobcard.xml',
        'views/checklist_name.xml',
        'views/quality_checklist.xml',
        'views/portal_view.xml'
    ],

    'installable' : True,
    'application' : False,
    'auto_install' : False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
