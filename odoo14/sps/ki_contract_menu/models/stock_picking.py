from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_set_quantities_to_reservation(self):
        for rec in self.move_ids_without_package:
            print('rrrrrrrrrrrr', rec)
            rec.quantity_done = rec.product_uom_qty
