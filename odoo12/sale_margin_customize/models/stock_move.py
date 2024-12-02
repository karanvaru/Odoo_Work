# -*- coding: utf-8 -*-
from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def write(self, vals):
        res = super(StockMove, self).write(vals)
        if 'price_unit' in vals and not self.env.context.get(
                'skip_sale_margin_sync', False):
            self.sale_margin_sync()
        return res

    def sale_margin_sync(self):
        for move in self.filtered(lambda m: (
                m.state == 'done' and m.sale_line_id and m._is_out())):
            move.sale_line_id.purchase_price = -move.price_unit
