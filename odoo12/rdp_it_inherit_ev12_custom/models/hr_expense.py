from odoo import api, _, fields, models
from odoo.exceptions import ValidationError


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    record_type_id = fields.Many2one(
        'record.type',
        string="Record Type",
        copy=False,
        track_visibility="onchange"
    )

    record_category_id = fields.Many2one(
        'record.category',
        string="Record Category",
        copy=False,
        track_visibility="onchange"
    )


    @api.multi
    def write(self, vals):
        res = super(HrExpense, self).write(vals)
        if self._context.get('from_es', False):
            return res

        for rec in self:
            rec.sheet_id.update({
                'record_type_id': rec.record_type_id.id,
                'record_category_id': rec.record_category_id.id,
            })
            rec.sheet_id.account_move_id.update({
                'record_type_id': rec.record_type_id.id,
                'record_category_id': rec.record_category_id.id,
            })
        return res

    def action_submit_expenses(self):
        res = super(HrExpense, self).action_submit_expenses()
        for rec in self:
            res['context'].update({
                'default_record_type_id': rec.record_type_id.id,
                'default_record_category_id': rec.record_category_id.id,
            })
        return res
