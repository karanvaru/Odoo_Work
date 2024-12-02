# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = "stock.move"

    record_type_id = fields.Many2one(
        'record.type',
        string="Record Type",
        track_visibility="onchange",
        copy=False,
        readonly=True
    )

    record_category_id = fields.Many2one(
        'record.category',
        string = "Record Category",
        track_visibility = "onchange",
        copy = False,
        readonly=True
    )

    @api.model
    def create(self, vals):
        stock_move = super(StockMove, self).create(vals)
        if stock_move.picking_id:
            stock_move.update({
                'record_type_id': stock_move.picking_id.record_type_id.id,
                'record_category_id': stock_move.picking_id.record_category_id.id
            })
        if not stock_move.picking_id:
            mrp = self.env['mrp.production'].sudo().search([('name', '=', stock_move.origin)])
            if mrp:
                stock_move.update({
                    'record_type_id': mrp.record_type_id.id,
                    'record_category_id': mrp.record_category_id.id
                })
        return stock_move

    @api.multi
    def write(self, vals):
        res = super(StockMove, self).write(vals)

        if self._context.get('from_uo', False):
            return res

        for  rec in self:
            moves = self.env['mrp.unbuild'].search([('name', '=', rec.reference)])
            if moves:
                moves.update({
                    'record_type_id': rec.record_type_id,
                    'record_category_id': rec.record_category_id,
                })

        return res