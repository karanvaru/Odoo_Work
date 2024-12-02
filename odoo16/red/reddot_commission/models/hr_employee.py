# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    department_manager_id = fields.Many2one(
        'hr.employee',
        string="Department Manager",
    )

    @api.onchange('department_id')
    def onchange_department(self):
        for record in self:
            record.department_manager_id = record.department_id.manager_id.id




class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    department_manager_id = fields.Many2one(
        'hr.employee',
        string="Department Manager",
    )


