# -*- coding: utf-8 -*-

from odoo import fields, models, api


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    inventory_value_type_je = fields.Many2one(
        'inventory.value.type.je',
        string="Inventory Value Type",
        track_visibility="onchange",
        copy=False
    )

    def _get_inventory_lines_values(self):
        inventory = super(StockInventory, self)._get_inventory_lines_values()
        for rec in inventory:
            rec.update({
                'inventory_value_type_je': self.inventory_value_type_je.id
            })
        return inventory

    def write(self, vals):
        super_res = super(StockInventory, self).write(vals)
        if 'inventory_value_type_je' in vals:
            if self.line_ids:
                for rec in self.line_ids:
                    rec.update({
                        'inventory_value_type_je': self.inventory_value_type_je.id
                    })
        return super_res


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    inventory_value_type_je = fields.Many2one(
        'inventory.value.type.je',
        string="Inventory Value Type",
        track_visibility="onchange",
        copy=False
    )
