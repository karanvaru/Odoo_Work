from odoo import api, models, fields, _


class MrpUnbuild(models.Model):
    _inherit = 'mrp.unbuild'

    record_type_id = fields.Many2one(
        'record.type',
        string="Record Type",
        track_visibility="onchange",
        copy=False,
        required=True
    )

    record_category_id = fields.Many2one(
        'record.category',
        string='Record Category',
        track_visibility="onchange",
        copy=False,
        required=True
    )

    @api.multi
    def write(self, vals):
        res = super(MrpUnbuild, self).write(vals)
        if self._context.get('stock_move', False):
            return res
        for rec in self:
            moves = self.env['stock.move'].sudo().search([('reference', '=', rec.name)])
            for move in moves:
                move.with_context(from_uo=True).update({
                    'record_type_id': rec.record_type_id.id,
                    'record_category_id': rec.record_category_id.id,
                })
                for journal in move.account_move_ids:
                    journal.with_context(from_uo=True).update({
                        'record_type_id': rec.record_type_id.id,
                        'record_category_id': rec.record_category_id.id,
                    })
        return res

