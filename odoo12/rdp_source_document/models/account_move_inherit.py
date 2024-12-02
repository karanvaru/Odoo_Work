from odoo import fields, models, api, _


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    custom_source_document = fields.Char(
        string='Source Document',
        copy=False,
        readonly=True
    )

    @api.model
    def create(self, vals):
        move = super(AccountMoveInherit, self).create(vals)
        if move.stock_move_id.picking_id.purchase_id:
            move.update({
                'custom_source_document': move.stock_move_id.picking_id.purchase_id.name
            })
        if move.stock_move_id.picking_id.sale_id:
            move.update({
                'custom_source_document': move.stock_move_id.picking_id.sale_id.name
            })
        return move



