from odoo import fields, models, api


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    record_type_id = fields.Many2one(
        'record.type',
        string="Record Type",
        track_visibility="onchange",
        store=True,
        copy=False,
        required=True
    )

    record_category_id = fields.Many2one(
        'record.category',
        string = "Record Category",
        track_visibility = "onchange",
        store = True,
        copy = False,
        required=True
    )

    def _prepare_move_values(self):
        vals = super(StockScrap, self)._prepare_move_values()
        vals.update({
            'record_type_id': self.record_type_id.id,
            'record_category_id': self.record_category_id.id
        })
        return vals

    def write(self, vals):
        super_res = super(StockScrap, self).write(vals)
        if 'record_type_id' in vals or 'record_category_id' in vals:
            for rec in self:
                if rec.move_id:
                    rec.move_id.with_context(from_sc=True).update({
                        'record_type_id': rec.record_type_id.id,
                        'record_category_id': rec.record_category_id.id
                    })
                    if rec.move_id.account_move_ids:
                        rec.move_id.account_move_ids.with_context(from_sc=True).update({
                            'record_type_id': rec.record_type_id.id,
                            'record_category_id': rec.record_category_id.id
                        })
        return super_res

    def action_validate(self):
        super_res = super(StockScrap, self).action_validate()
        self.ensure_one()
        if self.move_id:
            self.move_id.with_context(from_sc=True).update({
                'record_type_id': self.record_type_id.id,
                'record_category_id': self.record_category_id.id
            })
            if self.move_id.account_move_ids:
                self.move_id.account_move_ids.with_context(from_sc=True).update({
                    'record_type_id': self.record_type_id.id,
                    'record_category_id': self.record_category_id.id
                })        
        return super_res
        