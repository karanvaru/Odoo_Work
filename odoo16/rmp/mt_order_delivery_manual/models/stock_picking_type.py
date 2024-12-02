from odoo import api, fields, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    # def get_action_picking_tree_draft(self):
    #     return self._get_action('mt_order_delivery_manual.action_picking_tree_draft')
    #
    # def get_action_picking_tree_ready(self):
    #     return self._get_action('mt_order_delivery_manual.action_picking_tree_ready')
