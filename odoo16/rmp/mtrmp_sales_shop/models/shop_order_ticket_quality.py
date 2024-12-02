from odoo import models, fields, api


class ShopOrderTicketQuality(models.Model):
    _name = 'shop.order.ticket.quality'
    _description = "Returns Goods Quality Result"

    name = fields.Char(string="Ticket #", required=True)
