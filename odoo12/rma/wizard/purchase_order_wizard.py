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
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PurchaseOrderWizard(models.TransientModel):
    _name = 'purchase.order.wizard'
    _description = "Purchase Order wizard"

    @api.model
    def _get_qty(self, context={}):
        if self._context['active_model'] == "repair.management":
            result = self.env['repair.management'].browse(
                self._context['active_id'])
            return result.repair_qty
        else:
            result = self.env['rma.rma'].browse(self._context['active_id'])
            return result.refund_qty

    @api.model
    def _get_product(self, context={}):
        if self._context['active_model'] == "repair.management":
            result = self.env['repair.management'].browse(
                self._context['active_id'])
        else:
            result = self.env['rma.rma'].browse(self._context['active_id'])
        return result.product_id

    @api.model
    def _get_picking_in(self):
        company_id = self.env['res.users'].browse(self._uid).company_id.id
        types = self.env['stock.picking.type'].search(
            [('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)])
        if not types:
            types = self.env['stock.picking.type'].search(
                [('code', '=', 'incoming'), ('warehouse_id', '=', False)])
            if not types:
                raise osv.except_osv(_('Error!'), _(
                    "Make sure you have at least an incoming picking type defined"))
        return types[0]

    product_id = fields.Many2one(
        'product.product', "Product", default=_get_product, required=True)
    partner_id = fields.Many2one('res.partner', 'Supplier', domain=[
                                 ('supplier', '=', True)], required=True)
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', required=True,
                                   help="The pricelist sets the currency used for this purchase order. It also computes the supplier price for the selected products/quantities.")
    location_id = fields.Many2one(
        'stock.location', 'Destination', required=True, domain=[('usage', '<>', 'view')])
    product_qty = fields.Float(
        'Quantity Return', default=_get_qty, required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env[
                                 'res.company']._company_default_get('purchase.order'))
    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To',
                                      help="This will determine picking type of incoming shipment", required=True, default=_get_picking_in)

    @api.onchange('picking_type_id')
    def onchange_picking_type_id(self):
        if self.picking_type_id:
            picktype = self.env["stock.picking.type"].browse(
                self.picking_type_id.id)
            if picktype.default_location_dest_id:
                self.location_id = picktype.default_location_dest_id.id

    @api.multi
    def apply_and_view(self):
        order_id = self.apply()
        if order_id:
            view_id = self.env.ref('purchase.purchase_order_form').id
            context = self._context.copy()
            return {
                'name': 'PO Already Created',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(view_id, 'form')],
                'res_model': 'purchase.order',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'res_id': order_id.id,
            }

    @api.multi
    def apply(self):
        self.ensure_one()
        vals = {
            'partner_id': self.partner_id.id,
            # 'location_id': self.location_id.id,
            # 'pricelist_id': self.pricelist_id.id,
        }
        order_id = self.env["purchase.order"].create(vals)
        # raise Warning(order_id)
        order_line_vals = {
            'product_id': self.product_id.id,
            'product_qty': self.product_qty,
            # 'date_planned' : datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'product_uom': self.product_id.uom_po_id.id or self.product_id.uom_id.id,
            'order_id': order_id.id,
            'price_unit': 1.0,
            'date_planned': fields.datetime.now().date(),
            'name': 'self.product_id.name'
        }
        order_line_id = self.env["purchase.order.line"].create(order_line_vals)
        order_line_values = order_line_id.onchange_product_id()
        if self._context['active_model'] == "repair.management":
            result = self.env['repair.management'].browse(
                self._context['active_id'])
        else:
            result = self.env['rma.rma'].browse(self._context['active_id'])
        if order_id:
            result.write({'purchase_order_id': order_id.id})
        return(order_id)
