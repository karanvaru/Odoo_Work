# -*- coding: utf-8 -*-
from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    record_type_id = fields.Many2one(
        'record.type',
        string="Record Type",
        track_visibility="onchange",
        copy=False,
        required=True
    )

    record_category_id = fields.Many2one(
        'record.category',
        string= "Record Category",
        track_visibility = "onchange",
        copy = False,
        required=True
    )

    @api.model
    def _update_transaction_types(self):
        if self.picking_ids:
            self.picking_ids.with_context(from_so=True).update({
                'record_type_id': self.record_type_id.id,
                'record_category_id': self.record_category_id.id
            })
            self.picking_ids.mapped('move_lines').mapped('account_move_ids').with_context(from_so=True).update({
                'record_type_id': self.record_type_id.id,
                'record_category_id': self.record_category_id.id
            })

    def write(self, vals):
        super_res = super(SaleOrder, self).write(vals)
        if 'record_type_id' in vals or 'record_category_id' in vals:
            if self._context.get('invoice_sale', False):
                return super_res
            for rec in self:
                for invoice in rec.invoice_ids:
                    invoice.write({
                        'record_type_id': rec.record_type_id.id,
                        'record_category_id': rec.record_category_id.id
                    })
                rec._update_transaction_types()

        if 'so_gem_rp_id' in vals:
            for order in self:
                for invoice in order.invoice_ids:
                    invoice.write({
                        'so_gem_rp_id': order.so_gem_rp_id.id
                    })
        return super_res


    
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res.update({
            'record_type_id': self.record_type_id.id,
            'record_category_id': self.record_category_id.id
        })
        return res