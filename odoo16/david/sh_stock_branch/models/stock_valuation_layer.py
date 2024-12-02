# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import api, fields, models


class StockValuationLayerBranch(models.Model):
    _inherit = 'stock.valuation.layer'

    branch_id = fields.Many2one(
        'res.branch', string="Branch", default=lambda self: self.env.user.branch_id)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('stock_move_id'):
                stock_move = self.env['stock.move'].search(
                    [('id', '=', vals.get('stock_move_id'))], limit=1)

                if stock_move and stock_move.branch_id:
                    vals.update({'branch_id': stock_move.branch_id.id})

        line = super(StockValuationLayerBranch, self).create(vals_list)

        return line
