# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    inventory_value_type_je = fields.Many2one(
        'inventory.value.type.je',
        string="Inventory Value Type",
        track_visibility="onchange",
        copy=False
    )

    def _write(self, vals):
        res = super(StockPicking, self)._write(vals)
        for rec in self:
            if rec.move_ids_without_package:
                rec.move_ids_without_package.update({'inventory_value_type_je': rec.inventory_value_type_je.id})

        if self._context.get('from_mrp', False):
            return res

        if self._context.get('from_po', False):
            return res

        if self._context.get('from_so', False):
            return res

        if self._context.get('from_sc', False):
            return res

        if 'inventory_value_type_je' in vals:
            for rec in self:
                # if rec.move_ids_without_package:
                #     rec.move_ids_without_package.update({'inventory_value_type_je': rec.inventory_value_type_je.id})

                scrap = self.env['stock.scrap'].sudo().search([('picking_id', '=', rec.id)])
                if scrap:
                    scrap.update({'inventory_value_type_je': self.inventory_value_type_je})

                mrp = self.env['mrp.production'].sudo().search([('name', '=', rec.origin)])
                if mrp:
                    mrp.update({'inventory_value_type_je': self.inventory_value_type_je})
                    acc_move_lines = self.env['account.move.line'].search([('name', '=', rec.origin)])
                    acc_moves = acc_move_lines.mapped('move_id')
                    if acc_moves:
                        acc_moves.update({'inventory_value_type_je': rec.inventory_value_type_je.id})
                else:
                    if rec.purchase_id:
                        rec.purchase_id.update({'inventory_value_type_je': rec.inventory_value_type_je.id})
                        rec.purchase_id._update_transaction_types()

                    if rec.sale_id:
                        rec.sale_id.update({'inventory_value_type_je': rec.inventory_value_type_je.id})
                        rec.sale_id._update_transaction_types()

        if 'sale_id' in vals:
            for rec in self:
                if rec.sale_id.inventory_value_type_je:
                    rec.update({'inventory_value_type_je': rec.sale_id.inventory_value_type_je.id})
        return res


