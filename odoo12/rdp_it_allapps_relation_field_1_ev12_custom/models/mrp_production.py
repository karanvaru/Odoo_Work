# -*- coding: utf-8 -*-
from odoo import fields, models, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    inventory_value_type_je = fields.Many2one(
        'inventory.value.type.je',
        string="Inventory Value Type",
        track_visibility="onchange",
        copy=False
    )

    @api.model
    def create(self, vals):
        id = super(MrpProduction, self).create(vals)
        if id.picking_ids:
            id.picking_ids.with_context(from_mrp=True).update({
                'inventory_value_type_je': id.inventory_value_type_je.id
            })
        return id

    def write(self, vals):
        super_res = super(MrpProduction, self).write(vals)
        if 'inventory_value_type_je' in vals:
            for rec in self:
                if rec.picking_ids:
                    rec.picking_ids.with_context(from_mrp=True).update({
                        'inventory_value_type_je': rec.inventory_value_type_je.id
                    })
                acc_move_lines = self.env['account.move.line'].search([('name', '=', rec.name)])
                acc_moves = acc_move_lines.mapped('move_id')
                if acc_moves:
                    acc_moves.with_context(from_mo=True).update({'inventory_value_type_je': rec.inventory_value_type_je.id})

        return super_res

