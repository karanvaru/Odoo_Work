from odoo import models, fields, api, _
from datetime import date
from odoo.osv import expression


class SaleOrder(models.Model):
    _inherit = "sale.order"

    stock_request_id = fields.Many2one(
        'partner.stock.request',
        copy=False,
    )

    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        copy=False
    )



