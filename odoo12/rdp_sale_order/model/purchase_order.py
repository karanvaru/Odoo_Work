from odoo import models, fields, api
import datetime

class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'
    sale_order_po_id = fields.Many2one('sale.order',string='Sale Order PO', compute="compute_sale_order_po")

    @api.depends('agreement_id')
    def compute_sale_order_po(self):
        for rec in self:
             if rec.agreement_id:
                rec.sale_order_po_id = rec.agreement_id.sale_order_p_tender_id
