# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProjectProjectInherit(models.Model):
    _inherit = 'project.project'

    project_employee_rate_ids = fields.One2many(
        'project.employee.rate',
        'project_id',
        string="Employee Billing Rate"
    )


