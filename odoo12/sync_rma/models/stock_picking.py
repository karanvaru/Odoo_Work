# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class Picking(models.Model):
    _inherit = "stock.picking"
    _description = "Stock Picking"

    rma_issue_id = fields.Many2one('rma.issue', string="RMA", copy=False, readonly=True)
    return_rma_issue_id = fields.Many2one('rma.issue', string="RMA Return", copy=False, readonly=True)

    @api.model
    def create(self, vals):
        """
            Override method for update picking values
        """
        res = super(Picking, self).create(vals)
        if (self._context.get('rma_return') and self._context.get('rma_issue_id')) or (self._context.get('sales') and self._context.get('rma_issue_id')):
            rma_issue_id = self.env['rma.issue'].browse(self._context.get('rma_issue_id'))
            res['origin'] = rma_issue_id.name
            res['rma_issue_id'] = self._context.get('rma_issue_id')
        return res


class StockMove(models.Model):
    _inherit = "stock.move"
    _description = "stock move"

    serial_id = fields.Many2one('stock.production.lot', string="Serial No.", copy=False)
