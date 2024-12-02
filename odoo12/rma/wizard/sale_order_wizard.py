# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
import datetime


class SaleOrderWizard(models.TransientModel):
    _name = 'sale.order.wizard'

    @api.model
    def _get_qty(self, context={}):
        result = self.env['rma.rma'].browse(self._context['active_id'])
        return result.refund_qty

    @api.model
    def _get_product(self, context={}):
        result = self.env['rma.rma'].browse(self._context['active_id'])
        return result.product_id

    product_id = fields.Many2one(
        'product.product', "Product", default=_get_product, required=True)
    partner_id = fields.Many2one('res.partner', 'Customer', domain=[
                                 ('customer', '=', True)], required=True)
    # pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', required=True, help="The pricelist sets the currency used for this purchase order. It also computes the supplier price for the selected products/quantities.")
    # location_id =  fields.Many2one('stock.location', 'Destination', required=True, domain=[('usage','<>','view')])
    product_qty = fields.Float(
        'Quantity Return', default=_get_qty, required=True)

    @api.multi
    def apply(self):
        self.ensure_one()
        vals = {
            'partner_id': self.partner_id.id,
            'location_id': self.location_id.id,
            'pricelist_id': self.pricelist_id.id,
        }
        order_id = self.env["purchase.order"].create(vals)

        order_line_vals = {
            'product_id': self.product_id.id,
            'product_qty': self.product_qty,
            'order_id': order_id.id,
            'price_unit': 1.0,
            'date_planned': fields.datetime.now().date(),
            'name': 'self.product_id.name'
        }
        order_line_id = self.env["purchase.order.line"].create(order_line_vals)
        order_line_values = order_line_id.onchange_product_id(
            self.pricelist_id.id, self.product_id.id, self.product_qty, 1, self.partner_id.id)
        order_line_id.write(order_line_values["value"])
        if self._context['active_model'] == "repair.management":
            result = self.env['repair.management'].browse(
                self._context['active_id'])
        else:
            result = self.env['rma.rma'].browse(self._context['active_id'])
        if order_id:
            result.write({'purchase_order_id': order_id.id})
        return(order_id)
