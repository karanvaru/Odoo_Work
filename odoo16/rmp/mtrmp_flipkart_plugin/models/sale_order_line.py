# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderLineExtend(models.Model):
    _inherit = 'sale.order.line'

    flipkart_order_item_id = fields.Char(string="Ecommerce Order Item Id")

