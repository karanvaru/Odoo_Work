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
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
import datetime
import logging
_logger = logging.getLogger(__name__)


class ProductReturnWizard(models.TransientModel):
    _name = 'product.return.wizard'
    _description = "Product Return Wizard"

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

    @api.model
    def _get_sale_order(self):
        if self._context['active_model'] == "repair.management":
            result = self.env['repair.management'].browse(
                self._context['active_id'])
        else:
            result = self.env['rma.rma'].browse(self._context['active_id'])
        return result.order_id

    @api.model
    def _get_rma(self):
        if self._context['active_model'] == "repair.management":
            result = self.env['repair.management'].browse(
                self._context['active_id'])
            return result.rma_id.id
        else:
            result = self.env['rma.rma'].browse(self._context['active_id'])

            return result.id

    @api.model
    def _get_partner_location(self):
        result = self.env['rma.rma'].browse(self._context['active_id'])
        return result.partner_id.property_stock_customer

    sale_order_id = fields.Many2one(
        "sale.order", string="Sale Order", default=_get_sale_order)
    rma_id = fields.Many2one("rma.rma", string="RMA", default=_get_rma)
    product_id = fields.Many2one(
        'product.product', "Product", default=_get_product, required=True)
    des_location_id = fields.Many2one(
        'stock.location', 'Destination', required=True, domain=[('usage', '<>', 'view')])
    product_qty = fields.Float(
        'Quantity Return', default=_get_qty, required=True)
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type',
                                      help="This will determine picking type of incoming shipment", required=True, default=_get_picking_in)
    source_location_id = fields.Many2one(
        'stock.location', 'Source', required=True, domain=[('usage', '<>', 'view')], default=_get_partner_location,)
    priority = fields.Selection(PROCUREMENT_PRIORITIES, 'Priority', default='1')

    @api.onchange('picking_type_id')
    def onchange_picking_type_id(self):
        des_location_id = None
        if self.rma_id and self.rma_id.return_request_type == 'repair':
            repair_location_id = self.env['ir.default'].sudo().get('res.config.settings', 'repair_location_id')
            if repair_location_id:
                des_location_id = repair_location_id
        elif self.picking_type_id:
            picktype = self.env["stock.picking.type"].browse(
                self.picking_type_id.id)
            if picktype.default_location_dest_id:
                des_location_id = picktype.default_location_dest_id.id
        self.des_location_id = des_location_id

    @api.multi
    def apply(self):
        self.ensure_one()
        # Create new picking for returned products
        pick_type_id = self.picking_type_id.id
        new_picking = self.env["stock.picking"].create({
            'move_lines': [],
            'picking_type_id': pick_type_id,
            'state': 'draft',
            'origin': self.rma_id.name,
            'partner_id': self.rma_id.partner_id.id,
            'priority': self.priority,
            'location_id': self.source_location_id.id,
            'location_dest_id': self.des_location_id.id,
            'group_id': self.rma_id.order_id.procurement_group_id.id,
        })
        x = self.env["stock.move"].create({
            'product_id': self.product_id.id,
            'product_uom_qty': float(self.product_qty),
            'name': self.product_id.partner_ref,
            'product_uom': self.product_id.uom_id.id,
            'picking_id': new_picking.id,
            'state': 'draft',
            'origin': self.rma_id.name,
            'location_id': self.source_location_id.id,
            'location_dest_id': self.des_location_id.id,
            'picking_type_id': pick_type_id,
            'warehouse_id': self.picking_type_id.warehouse_id.id,
            'procure_method': 'make_to_stock',
            'group_id': self.rma_id.order_id.procurement_group_id.id,
        })
        new_picking.action_confirm
        new_picking.action_assign()

        new_picking.sale_id = self.sale_order_id.id
        self.env["rma.rma"].browse(self.rma_id.id).write(
            {"picking_id": new_picking.id})
        x = self.env["sale.order"].browse(self.sale_order_id.id)

        return new_picking, pick_type_id
