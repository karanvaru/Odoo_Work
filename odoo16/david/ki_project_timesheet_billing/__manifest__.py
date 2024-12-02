# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Ki Project Timesheet Billing",
    'summary': """Project Timesheet Billing""",
    'description': """Project Timesheet Billing""",
    "version": "1.0.0",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'OPL-1',
    "depends": [
        'job_card', 'project','ki_job_card_extend'
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/project_project_inherit_view.xml',
        'views/res_config_settting_view.xml',
    ],

    "application": False,
    'installable': True,
}
