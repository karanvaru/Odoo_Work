from odoo import fields,models,api,_
from datetime import datetime, timedelta,date


class AccountInvoice(models.Model):
    _inherit ="account.invoice"

    sale_order_po_id = fields.Many2one('sale.order', string="Sale Order PO", compute="compute_sale_order_po")

    @api.depends('invoice_line_ids.purchase_id')
    def compute_sale_order_po(self):
        for rec in self:
            for record in rec.invoice_line_ids:
                if record.purchase_id:
                    rec.sale_order_po_id = record.purchase_id.sale_order_po_id.id