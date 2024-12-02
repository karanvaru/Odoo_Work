from odoo import models, fields, api


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    is_default_manager = fields.Boolean(
        string="Is Default Manager",
        copy=False,
    )

    @api.model
    def default_get(self, default_fields):
        values = super().default_get(default_fields)
        employee = self.search([('is_default_manager', '=', True)], limit=1)
        if employee:
            values['parent_id'] = employee.id
        return values
