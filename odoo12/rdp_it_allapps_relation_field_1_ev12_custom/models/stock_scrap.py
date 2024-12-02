from odoo import fields, models, api


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    inventory_value_type_je = fields.Many2one(
        'inventory.value.type.je',
        string="Inventory Value Type",
        track_visibility="onchange",
        store=True,
        copy=False,
    )

    def _prepare_move_values(self):
        vals = super(StockScrap, self)._prepare_move_values()
        vals.update({
            'inventory_value_type_je': self.inventory_value_type_je.id
        })
        return vals

    def write(self, vals):
        super_res = super(StockScrap, self).write(vals)
        if 'inventory_value_type_je' in vals:
            for rec in self:
                if rec.move_id:
                    rec.move_id.with_context(from_sc=True).update({
                        'inventory_value_type_je': rec.inventory_value_type_je.id
                    })
                    if rec.move_id.account_move_ids:
                        rec.move_id.account_move_ids.with_context(from_sc=True).update({
                            'inventory_value_type_je': rec.inventory_value_type_je.id
                        })
        return super_res

    def action_validate(self):
        super_res = super(StockScrap, self).action_validate()
        self.ensure_one()
        if self.move_id:
            self.move_id.with_context(from_sc=True).update({
                'inventory_value_type_je': self.inventory_value_type_je.id
            })
            if self.move_id.account_move_ids:
                self.move_id.account_move_ids.with_context(from_sc=True).update({
                    'inventory_value_type_je': self.inventory_value_type_je.id
                })        
        return super_res
        