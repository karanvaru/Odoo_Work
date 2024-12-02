from odoo import models, fields, api, _


class AccountMoveLineInherit(models.Model):
    _inherit = "account.move.line"

    amount_gross_profit = fields.Float(
        string="Gross Profit",
        compute='_compute_amount_gross_profit',
        store=True
    )

    @api.depends('price_unit', 'quantity', 'product_id.standard_price')
    def _compute_amount_gross_profit(self):
        for rec in self:
            rec.amount_gross_profit = (rec.price_unit - rec.product_id.standard_price) * rec.quantity
