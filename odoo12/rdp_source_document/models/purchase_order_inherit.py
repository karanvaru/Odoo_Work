from odoo import fields, models, api, _


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    def set_source_document(self):
        for rec in self:
            rec.picking_ids.mapped('move_lines').mapped('account_move_ids').update({
                'custom_source_document': rec.name
            })
            rec.invoice_ids.mapped('move_id').update({
                'custom_source_document': rec.name
            })
