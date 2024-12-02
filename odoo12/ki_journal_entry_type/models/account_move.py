# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    transaction_type_id = fields.Many2one(
        'journal.entry.type',
        string="JE Type",
        track_visibility="onchange",
        copy=False
    )

    @api.model
    def create(self, vals):
        id = super(AccountMove, self).create(vals)
        if id.stock_move_id and id.stock_move_id.picking_id:
            id.update({
                'transaction_type_id': id.stock_move_id.picking_id.transaction_type_id.id
            })
        return id
