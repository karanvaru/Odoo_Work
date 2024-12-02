# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class Picking(models.Model):
    _inherit = "stock.picking"
    _description = "Stock Picking"

    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket', copy=False, readonly=True)

    @api.model
    def create(self, vals):
        """
            Override method for update picking values
        """
        res = super(Picking, self).create(vals)
        if (self._context.get('rma_return') and self._context.get('rma_issue_id')) or (self._context.get('sales') and self._context.get('rma_issue_id')):
            rma_issue_id = self.env['rma.issue'].browse(self._context.get('rma_issue_id'))
            res['ticket_id'] = rma_issue_id.ticket_id and rma_issue_id.ticket_id.id or False
        return res
