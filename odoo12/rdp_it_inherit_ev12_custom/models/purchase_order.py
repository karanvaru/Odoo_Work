# -*- coding: utf-8 -*-
from odoo import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    record_type_id = fields.Many2one(
        'record.type',
        string="Record Type",
        track_visibility="onchange",
        copy=False,
        required=True
    )

    record_category_id = fields.Many2one(
        'record.category',
        string="Record Category",
        track_visibility="onchange",
        copy=False,
        required=True
    )


    @api.model
    def _prepare_picking(self):
        vals = super(PurchaseOrder, self)._prepare_picking()
        vals.update({
            'record_type_id': self.record_type_id.id,
            'record_category_id': self.record_category_id.id
        })
        return vals

    @api.model
    def _update_transaction_types(self):
        if self.picking_ids:
            self.picking_ids.with_context(from_po=True).update({
                'record_type_id': self.record_type_id.id,
                'record_category_id': self.record_category_id.id
            })
            self.picking_ids.mapped('move_lines').mapped('account_move_ids').with_context(from_po=True).update({
                'record_type_id': self.record_type_id.id,
                'record_category_id': self.record_category_id.id
            })

    def write(self, vals):
        super_res = super(PurchaseOrder, self).write(vals)
        if 'record_type_id' in vals or 'record_category_id' in vals:
            if self._context.get('invoice_purchase', False):
                return super_res
            for rec in self:
                for purchase in rec.invoice_ids:
                    purchase.write({
                        'record_type_id': rec.record_type_id.id,
                        'record_category_id': rec.record_category_id.id
                    })
                rec._update_transaction_types()
        return super_res
