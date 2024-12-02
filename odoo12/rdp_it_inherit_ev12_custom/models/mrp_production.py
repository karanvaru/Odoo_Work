# -*- coding: utf-8 -*-
from odoo import fields, models, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    record_type_id = fields.Many2one(
        'record.type',
        string="Record type",
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
    def create(self, vals):
        new_production = super(MrpProduction, self).create(vals)
        if new_production.picking_ids:
            new_production.picking_ids.with_context(from_mrp=True).update({
                'record_type_id': new_production.record_type_id.id,
                'record_category_id': new_production.record_category_id.id
            })
        return new_production

    def write(self, vals):
        super_res = super(MrpProduction, self).write(vals)
        if 'record_type_id' in vals or 'record_category_id' in vals:
            for rec in self:
                if rec.picking_ids:
                    rec.picking_ids.with_context(from_mrp=True).update({
                        'record_type_id': rec.record_type_id.id,
                        'record_category_id': rec.record_category_id.id
                    })
                acc_move_lines = self.env['account.move.line'].search([('name', '=', rec.name)])
                acc_moves = acc_move_lines.mapped('move_id')
                if acc_moves:
                    acc_moves.with_context(from_mo=True).update({
                        'record_type_id': rec.record_type_id.id,
                        'record_category_id': rec.record_category_id.id
                    })

        return super_res