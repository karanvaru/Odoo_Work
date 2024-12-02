from odoo import fields, models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    record_type_id = fields.Many2one(
        'record.type',
        string="Record Type",
        track_visibility="onchange",
        related="move_id.record_type_id",
        store=True,
        copy=False,
    )

    record_category_id = fields.Many2one(
        'record.category',
        string="Record Category",
        track_visibility="onchange",
        related="move_id.record_category_id",
        store=True,
        copy=False
    )



#     def write(self, vals):
#         super_res = super(AccountMoveLine, self).write(vals)
#         if self._context.get('from_account', False):
#             return super_res
#         if 'record_type_id' in vals:
#             for rec in self:
#                 if rec.move_id:
#                     rec.move_id.with_context(from_mo_li=True).update({
#                         'record_type_id': rec.record_type_id.id
#                     })
#         return super_res

