# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = "stock.move"

    inventory_value_type_je = fields.Many2one(
        'inventory.value.type.je',
        string="Inventory Value Type",
        track_visibility="onchange",
        copy=False,
        reaonly=True
    )

    @api.model
    def create(self, vals):
        stock_move = super(StockMove, self).create(vals)
        if stock_move.picking_id:
            stock_move.update({
                'inventory_value_type_je': stock_move.picking_id.inventory_value_type_je.id
            })
        if not stock_move.picking_id:
            mrp = self.env['mrp.production'].sudo().search([('name', '=', stock_move.origin)])
            if mrp:
                stock_move.update({
                    'inventory_value_type_je': mrp.inventory_value_type_je.id
                })
        return stock_move
