from odoo import models, fields, api, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    lot_ids = fields.Many2many(
         'stock.lot',
         compute='_compute_lot_ids',
         string='Serial Numbers',
         readonly=False
    )

    @api.depends('sale_line_ids', 'sale_line_ids.move_ids', 'sale_line_ids.move_ids.lot_ids')
    def _compute_lot_ids(self):
        for line in self:
            if line.sale_line_ids and line.sale_line_ids.move_ids and line.sale_line_ids.move_ids.lot_ids:
                line.update({
                    'lot_ids': [(6, 0, line.sale_line_ids.move_ids.lot_ids.ids)]
                })

