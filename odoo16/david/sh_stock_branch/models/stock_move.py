# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import api, fields, models


class StockMoveBranch(models.Model):
    _inherit = 'stock.move'

    branch_id = fields.Many2one(
        'res.branch', string="Branch", default=lambda self: self.env.user.branch_id)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('picking_id'):
                picking = self.env['stock.picking'].search(
                    [('id', '=', vals.get('picking_id'))], limit=1)
                if picking and picking.branch_id:
                    vals.update({'branch_id': picking.branch_id.id})

            if vals.get('inventory_id'):
                inventory = self.env['stock.inventory'].search(
                    [('id', '=', vals.get('inventory_id'))], limit=1)
                if inventory and inventory.branch_id:
                    vals.update({'branch_id': inventory.branch_id.id})

            if vals.get('origin'):
                scrap = self.env['stock.scrap'].search(
                    [('name', '=', vals.get('origin'))], limit=1)

                if scrap and scrap.branch_id:
                    vals.update({'branch_id': scrap.branch_id.id})

        move = super(StockMoveBranch, self).create(vals_list)

        return move


class StockMoveLineBranch(models.Model):
    _inherit = 'stock.move.line'

    branch_id = fields.Many2one(
        'res.branch', string="Branch", default=lambda self: self.env.user.branch_id)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('picking_id'):
                stock_move_line = self.env['stock.picking'].search(
                    [('id', '=', vals.get('picking_id'))], limit=1)

                if stock_move_line and stock_move_line.branch_id:
                    vals.update({'branch_id': stock_move_line.branch_id.id})

            if vals.get('move_id'):
                move = self.env['stock.move'].search(
                    [('id', '=', vals.get('move_id'))], limit=1)

                if move and move.branch_id:
                    vals.update({'branch_id': move.branch_id.id})

        line = super(StockMoveLineBranch, self).create(vals_list)

        return line
