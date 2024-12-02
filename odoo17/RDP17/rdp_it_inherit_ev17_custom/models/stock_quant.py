# -*- coding: utf-8 -*-

from odoo import fields, models, api


class StockInventory(models.Model):
    _inherit = 'stock.quant'

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

    def _get_inventory_lines_values(self):
        inventory = super(StockInventory, self)._get_inventory_lines_values()
        for rec in inventory:
            rec.update({
                'record_type_id': self.record_type_id.id,
                'record_category_id': self.record_category_id.id
            })
        return inventory

    def write(self, vals):
        super_res = super(StockInventory, self).write(vals)
        if 'record_type_id' in vals or 'record_category_id' in vals:
            if self.line_ids:
                for rec in self.line_ids:
                    rec.update({
                        'record_type_id': self.record_type_id.id,
                        'record_category_id': self.record_category_id.id
                    })
        return super_res
#
# class StockInventoryLine(models.Model):
#     _inherit = 'stock.quant.line'
#
#     record_type_id = fields.Many2one(
#         'inventory.value.type.je',
#         string="Inventory Value Type",
#         track_visibility="onchange",
#         copy=False
#     )
