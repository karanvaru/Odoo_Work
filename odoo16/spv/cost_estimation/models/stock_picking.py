# -*- coding: utf-8 -*-
import logging

from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    account_analytic_id = fields.Many2one('account.analytic.account', string='Project')

class StockMove(models.Model):
    _inherit = "stock.move"

    account_analytic_id = fields.Many2one('account.analytic.account',
                                          related='picking_id.account_analytic_id',
                                          string='Project')

    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id, description):
        res = super(StockMove, self)._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
        for line in res:
            if self.account_analytic_id:
                line[2].update({"analytic_account_id": self.account_analytic_id.id})
        return res


