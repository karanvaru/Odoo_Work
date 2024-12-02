# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Job Card Extend",
    'summary': """Job Card Extend""",
    'description': """Job Card Extend""",
    "version": "1.21.3",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "depends": [
        'web',
        'project',
        'job_card',
        'job_card_portal_odoo',
        'garage_management_odoo',
        'project_task_material_requisition',
    ],
    "data": [
        'data/jobcost_sequence.xml',
        'report/report_jobcard.xml',
        'report/job_card_report_portal.xml',
        'report/report_template.xml',
        'report/report_quo_inv.xml',
        'views/job_card_view.xml',
        'views/material_purchase_requisition.xml',
        'views/product_view.xml',
        'views/portal_view.xml',
        # 'views/job_card_portal.xml',
    ],
    "application": False,
    'installable': True,
}
