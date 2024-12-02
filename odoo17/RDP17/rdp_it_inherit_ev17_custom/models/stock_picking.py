# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    record_type_id = fields.Many2one(
        'record.type',
        string="Record Type",
        track_visibility="onchange",
        copy=False
    )

    record_category_id = fields.Many2one(
        'record.category',
        string = "Record Category",
        track_visibility = "onchange",
        copy = False
    )

    def _write(self, vals):
        res = super(StockPicking, self)._write(vals)

        if self.move_ids_without_package:
            self.move_ids_without_package.update({'record_type_id': self.record_type_id.id})
            self.move_ids_without_package.update({'record_category_id': self.record_category_id.id})

        if self._context.get('from_mrp', False):
            return res

        if self._context.get('from_po', False):
            return res

        if self._context.get('from_so', False):
            return res

        if self._context.get('from_sc', False):
            return res

        if 'record_type_id' in vals or 'record_category_id' in vals:
            for rec in self:
                scrap = self.env['stock.scrap'].sudo().search([('picking_id', '=', rec.id)])
                if scrap:
                    scrap.update({
                        'record_type_id': rec.record_type_id.id,
                        'record_category_id': rec.record_category_id.id
                    })

                mrp = self.env['mrp.production'].sudo().search([('name', '=', rec.origin)])
                if mrp:
                    mrp.update({
                        'record_type_id': rec.record_type_id.id,
                        'record_category_id': rec.record_category_id.id
                    })
                    acc_move_lines = self.env['account.move.line'].search([('name', '=', rec.origin)])
                    acc_moves = acc_move_lines.mapped('move_id')
                    if acc_moves:
                        acc_moves.update({
                            'record_type_id': rec.record_type_id.id,
                            'record_category_id': rec.record_category_id.id
                        })
                else:
                    if rec.purchase_id:
                        rec.purchase_id.update({
                            'record_type_id': rec.record_type_id.id,
                            'record_category_id': rec.record_category_id.id
                        })
                        rec.purchase_id._update_transaction_types()

                    if rec.sale_id:
                        rec.sale_id.update({
                            'record_type_id': rec.record_type_id.id,
                            'record_category_id': rec.record_category_id.id
                        })
                        rec.sale_id._update_transaction_types()

        if 'sale_id' in vals:
            for rec in self:
                if rec.sale_id.record_type_id:
                    rec.update({
                        'record_type_id': rec.sale_id.record_type_id.id,
                        'record_category_id': rec.sale_id.record_category_id.id
                    })
        return res