from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        res = super(StockMove, self)._get_new_picking_values()
        res['original_order_lines'] = [(6, 0, self.sale_line_id.ids)]
        return res
