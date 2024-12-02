from odoo import fields, models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    inventory_value_type_je = fields.Many2one(
        'inventory.value.type.je',
        string="Inventory Value Type",
        track_visibility="onchange",
        related="move_id.inventory_value_type_je",
        store=True,
        copy=False,
    )

#     def write(self, vals):
#         super_res = super(AccountMoveLine, self).write(vals)
#         if self._context.get('from_account', False):
#             return super_res
#         if 'inventory_value_type_je' in vals:
#             for rec in self:
#                 if rec.move_id:
#                     rec.move_id.with_context(from_mo_li=True).update({
#                         'inventory_value_type_je': rec.inventory_value_type_je.id
#                     })
#         return super_res

