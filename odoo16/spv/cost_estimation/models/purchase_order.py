# -*- coding: utf-8 -*-

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_confirm(self, force=False):
        res = super(PurchaseOrder, self).button_confirm()
        for line in self.order_line:
            line.product_id.estimated_cost = line.price_unit
        return res
