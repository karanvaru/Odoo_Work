# -*- coding: utf-8 -*-
from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    inventory_value_type_je = fields.Many2one(
        'inventory.value.type.je',
        string="Inventory Value Type",
        track_visibility="onchange",
        copy=False
    )

    @api.model
    def _update_transaction_types(self):
        if self.picking_ids:
            self.picking_ids.with_context(from_so=True).update({
                'inventory_value_type_je': self.inventory_value_type_je.id
            })
            self.picking_ids.mapped('move_lines').mapped('account_move_ids').with_context(from_so=True).update({
                'inventory_value_type_je': self.inventory_value_type_je.id
            })

    def write(self, vals):
        super_res = super(SaleOrder, self).write(vals)
        if 'inventory_value_type_je' in vals:
            for rec in self:
                rec._update_transaction_types()
        return super_res
