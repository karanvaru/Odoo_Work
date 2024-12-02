# -*- coding: utf-8 -*-
from odoo import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    transaction_type_id = fields.Many2one(
        'journal.entry.type',
        string="JE Type",
        track_visibility="onchange",
        copy=False
    )

    @api.model
    def _prepare_picking(self):
        vals = super(PurchaseOrder, self)._prepare_picking()
        vals.update({'transaction_type_id': self.transaction_type_id.id})
        return vals
