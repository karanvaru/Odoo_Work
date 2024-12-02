from odoo import models, fields, api, _


class HrExpenseInherit(models.Model):
    _inherit = 'hr.expense'

    department_id = fields.Many2one(
        'hr.department',
        related="employee_id.department_id",
        string='Department',
        store=True
    )
