from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    record_type_id = fields.Many2one(
        'record.type',
        string="Record Type",
        copy=False,
        track_visibility="onchange",
    )

    record_category_id = fields.Many2one(
        'record.category',
        string="Record Category",
        copy=False,
        track_visibility="onchange",

    )

    @api.multi
    def write(self, vals):
        res = super(HrExpenseSheet, self).write(vals)
        if self._context.get('expense_move', False):
            return res
        for rec in self:
            for ex in rec.expense_line_ids:
                ex.with_context(from_es=True).update({
                    'record_type_id': rec.record_type_id.id,
                    'record_category_id': rec.record_category_id.id,
                })
            rec.account_move_id.update({
                'record_type_id': rec.record_type_id.id,
                'record_category_id': rec.record_category_id.id,
            })
        return res

    @api.multi
    def approve_expense_sheets(self):
        res = super(HrExpenseSheet, self).approve_expense_sheets()
        for ex in self.expense_line_ids:
            if not ex.record_type_id or not ex.record_category_id:
                raise ValidationError("Add Record Type Or Record Category On Expense Before Approve.")
        return res
