from odoo import models, fields, api


class PurchaseTender(models.Model):
    _inherit = 'purchase.agreement'

    sale_order_p_tender_id = fields.Many2one('sale.order',string='Sale Order PTender', track_visibility="always")
