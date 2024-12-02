from odoo import models, fields, api


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    unit_amount = fields.Float(
        'Quantity',
        default=0.0,
        compute='_compute_unit_amount',
        store=True
    )

    @api.depends('time_in', 'time_out')
    def _compute_unit_amount(self):
        for rec in self:
            rec.unit_amount = rec.time_out - rec.time_in
