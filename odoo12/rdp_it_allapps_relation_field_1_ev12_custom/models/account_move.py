# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    inventory_value_type_je = fields.Many2one(
        'inventory.value.type.je',
        string="Inventory Value Type",
        track_visibility="onchange",
        copy=False
    )

    @api.model
    def create(self, vals):
        id = super(AccountMove, self).create(vals)
        if id.stock_move_id:
            if id.stock_move_id.picking_id:
                id.update({
                    'inventory_value_type_je': id.stock_move_id.picking_id.inventory_value_type_je.id
                })
            elif id.stock_move_id.production_id:
                id.update({
                    'inventory_value_type_je': id.stock_move_id.production_id.inventory_value_type_je.id
                })
            elif id.stock_move_id.created_production_id:
                id.update({
                    'inventory_value_type_je': id.stock_move_id.created_production_id.inventory_value_type_je.id
                })
            elif id.stock_move_id.raw_material_production_id:
                id.update({
                    'inventory_value_type_je': id.stock_move_id.raw_material_production_id.inventory_value_type_je.id
                })

        return id

    def _write(self, vals):
        res = super(AccountMove, self)._write(vals)
#         if 'inventory_value_type_je' in vals:
#             for rec in self:
#                 if rec.line_ids:
#                     rec.line_ids.with_context(from_account=True)._write({
#                         'inventory_value_type_je': rec.inventory_value_type_je.id
#                     })

        if self._context.get('from_po', False):
            return res

        if self._context.get('from_so', False):
            return res

        if self._context.get('from_mo', False):
            return res

        # if self._context.get('from_mrp', False):
        #     return res

        if 'inventory_value_type_je' in vals:
            for rec in self:
                picking = rec.stock_move_id.picking_id
                if picking:
                    sale_id = picking.sale_id
                    if sale_id:
                        sale_id.with_context(from_account=True).write({
                            'inventory_value_type_je': rec.inventory_value_type_je.id
                        })

                    purchase_id = picking.purchase_id
                    if purchase_id:
                        purchase_id.with_context(from_account=True).write({
                            'inventory_value_type_je': rec.inventory_value_type_je.id
                        })
                else:
                    production_id = False
                    if rec.stock_move_id.production_id:
                        production_id = rec.stock_move_id.production_id
                    elif rec.stock_move_id.created_production_id:
                        production_id = rec.stock_move_id.created_production_id
                    elif rec.stock_move_id.raw_material_production_id:
                        production_id = rec.stock_move_id.raw_material_production_id
                    if production_id:
                        production_id.with_context(from_account=True).write({
                            'inventory_value_type_je': rec.inventory_value_type_je.id
                        })

                    # mrp = self.env['mrp.production'].sudo().search([('name', '=', picking.origin)])
                    # mrp.with_context(from_account=True).write({'inventory_value_type_je': self.inventory_value_type_je})
        return res


