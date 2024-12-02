from odoo import models, fields, api


class HrLeavesInherited(models.Model):
    _inherit = 'hr.leave'

    spoc_id = fields.Many2one("hr.employee", 'SPOC', compute='compute_spoc', store=True)

    @api.depends('employee_id')
    def compute_spoc(self):
        for rec in self:
            rec.spoc_id = rec.employee_id.coach_id.id
