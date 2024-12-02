# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': "Field Service Management",
    'currency': 'EUR',
    'license': 'Other proprietary',
    'price': 49.0,
    'summary': """Field Service Odoo App Only for Odoo Community Edition.""",
    'description': """This app allows the project user/technician to create 
    field service tasks. Sales estimates can also be created, managed, and 
    sent to customers and then confirmed and approved by the team and customers
    to do a signature on an estimate on the portal of your website. 
    Project users  / Technicians / Field Engineers can create as many material
    requisitions for projects and field services they are working on.
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "www.probuse.com",
    'support': 'contact@probuse.com',
    'version': '1.1.1',
    'category' : 'Services/Project',
    'images' : ['static/description/img1.png'],
    'depends': [
    'project',
    'odoo_sale_estimates',
    'sale_estimate_customer_approve_sign',
    'project_task_material_requisition',
    'sale_estimate_customer_portal',
    ],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/field_service_management_odoo/1346',
    'data':[
        'views/project_task.xml',
        'views/sale_estimate.xml',
    ],
    'installable' : True,
    'application' : False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
