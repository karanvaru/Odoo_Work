# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProjectEmployeeRate(models.Model):
    _name = "project.employee.rate"
    _description = 'Project Employee Rate'

    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee",
        required=True
    )

    hourly_rate = fields.Float(
        string='Rate/Hour',
    )

    project_id = fields.Many2one(
        'project.project',
        string="Project",
    )
