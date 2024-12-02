from odoo import fields, models, api, _


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    custom_source_document = fields.Char(
        string='Source Document',
        copy=False,
        readonly=True,
        related="move_id.custom_source_document"
    )
