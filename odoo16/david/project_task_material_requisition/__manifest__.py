# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Material Requisition for Project and Task Integration",
    'version': '3.1.9',
    'category' : 'Services/Project',
    'price': 29.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This app allow you to select Project and Task on Material Purchase Requisition.""",
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/mrimg1.jpg'],
    'description': """
This app allow you to set Project and Task on Material Purchase Requisition.
Project Material Requisition Smart Button
Task Material Purchase Requisition
Material Purchase Requisition Group By Project
Material Purchase Requisition Group By Task
Material Purchase Requisition
Material requisition
    """,
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/project_task_material_requisition/951',#'https://youtu.be/WI-kTPBVPDs',
    'depends': [
                'project',
                'material_purchase_requisitions',
                ],
    'data':[
       'views/material_purchase_requisition_view.xml',
       'views/project_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
