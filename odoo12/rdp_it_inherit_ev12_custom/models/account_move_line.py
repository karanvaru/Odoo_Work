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



