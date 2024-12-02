from odoo import api, fields, _, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    so_gem_rp_id = fields.Many2one(
        'res.partner', 
        string="SO Gem RP",
        readonly=True
    )

    record_type_id = fields.Many2one(
        'record.type',
        string="Record Type",
        track_visibility="onchange",
        copy=False,
        required=True
    )

    record_category_id = fields.Many2one(
        'record.category',
        string="Record Category",
        track_visibility="onchange",
        copy=False,
        required=True
    )

    


    @api.model
    def default_get(self, fields):
        res = super(AccountInvoice, self).default_get(fields)
        if 'purchase_id' in res:
            purchase = self.env['purchase.order'].browse(int(res['purchase_id']))
            res.update({
                'record_type_id': purchase.record_type_id.id,
                'record_category_id': purchase.record_category_id.id
            })
        return res

    def write(self, vals):
        res = super(AccountInvoice, self).write(vals)
        if 'record_type_id' in vals or 'record_category_id' in vals:
            if self._context.get('invoice_move', False):
                return res
            for rec in self:
                rec.move_id.with_context(invoice_move=True).write({
                    'record_type_id': rec.record_type_id.id,
                    'record_category_id': rec.record_category_id.id
                })
                source_orders = rec.invoice_line_ids.mapped('sale_line_ids').mapped('order_id')
                source_orders.with_context(invoice_sale=True).write({
                    'record_type_id': rec.record_type_id.id,
                    'record_category_id': rec.record_category_id.id
                })
                purchase = rec.invoice_line_ids.mapped('purchase_line_id').mapped('order_id')
                purchase.with_context(invoice_purchase=True).write({
                    'record_type_id': rec.record_type_id.id,
                    'record_category_id': rec.record_category_id.id
                })
                for pick in source_orders.picking_ids:
                    pick.with_context(invoice_sale_picking=True).write({
                        'record_type_id': rec.record_type_id.id,
                        'record_category_id': rec.record_category_id.id
                    })
                for purc in purchase.picking_ids:
                    purc.with_context(invoice_purchase_picking=True).write({
                        'record_type_id': rec.record_type_id.id,
                        'record_category_id': rec.record_category_id.id
                    })

        return res

    @api.multi
    def action_move_create(self):
        result = super(AccountInvoice, self).action_move_create()
        for rec in self:
            rec.move_id.update({
                'record_type_id': rec.record_type_id.id,
                'record_category_id': rec.record_category_id.id
            })

        return result
