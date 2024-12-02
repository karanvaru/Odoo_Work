from odoo import api, fields, models, _

class StockMove(models.Model):
    _inherit = "stock.move"
    
    sale_price_unit = fields.Float(string='Price Unit',
        store=True, readonly=True, compute='_compute_price_unit')
    
    @api.multi
    @api.depends('sale_line_id')
    def _compute_price_unit(self):
        for move in self:
            if move.sale_line_id:
                move.sale_price_unit = move.sale_line_id.price_unit