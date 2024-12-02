# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    transaction_type_id = fields.Many2one(
        'journal.entry.type',
        string="JE Type",
        track_visibility="onchange",
        copy=False
    )

    def _write(self, vals):
        res = super(StockPicking, self)._write(vals)
        if 'transaction_type_id' in vals:
            account_move = self.env['account.move'].search([('ref' ,'=',self.name)])
            print("+aaaaaaaaaaccount_moveaccount_move",account_move)
            # for rec in account_move:
            if account_move:
                account_move.transaction_type_id = self.transaction_type_id


            if self.sale_id:
                if self.sale_id.transaction_type_id:
                    self.sale_id.transaction_type_id = self.transaction_type_id
            if self.purchase_id:
                if self.purchase_id.transaction_type_id:
                    self.purchase_id.transaction_type_id = self.transaction_type_id




        if 'sale_id' in vals:
            for rec in self:
                if rec.sale_id.transaction_type_id:
                    rec.transaction_type_id = rec.sale_id.transaction_type_id.id
        return res
