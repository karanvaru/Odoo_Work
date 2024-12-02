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
import odoo.osv.osv as osv

import datetime
import logging
_logger = logging.getLogger(__name__)


class NewDeliveryOrderWizard(models.TransientModel):
    _name = 'new.delivery.order.wizard'
    _description = "New Delivery Order Wizard"

    @api.model
    def default_get(self, default_fields):
        res = super(NewDeliveryOrderWizard, self).default_get(default_fields)
        rma_obj = self.env['rma.rma'].browse(self._context['active_id'])
        if rma_obj:
            is_repaired = True if rma_obj.mrp_repair_id else False
            company_id = self.env.user.company_id.id
            picking_type = self.env['stock.picking.type'].search([('code', '=', 'outgoing'), ('warehouse_id.company_id', '=', company_id)], limit=1)
            if not picking_type:
                picking_type = self.env['stock.picking.type'].search([('code', '=', 'outgoing'), ('warehouse_id', '=', False)], limit=1)
                if not picking_type:
                    raise osv.except_osv(_('Error!'), _("Make sure you have at least an outgoing picking type defined"))

            source_location_id = None
            des_location_id = rma_obj.partner_id.property_stock_customer.id
            if is_repaired:
                mrp_repair_id = self.env["repair.order"].browse(int(rma_obj.mrp_repair_id))
                if mrp_repair_id:
                    source_location_id = mrp_repair_id.location_id.id
                    des_location_id = mrp_repair_id.location_dest_id.id
            elif picking_type:
                if picking_type.default_location_dest_id:
                    des_location_id = picking_type.default_location_dest_id.id
                if picking_type.default_location_src_id:
                    source_location_id = picking_type.default_location_src_id.id
            res.update({
                'rma_id': rma_obj.id,
                'source_location_id': source_location_id,
                'des_location_id': des_location_id,
                'picking_type_id': picking_type.id,
                'is_repaired': is_repaired,
                'product_id': rma_obj.product_id.id,
                'product_qty': rma_obj.refund_qty,
                'sale_order_id': rma_obj.order_id.id,
            })
        return res

    sale_order_id = fields.Many2one("sale.order", string="Sale Order")
    rma_id = fields.Many2one("rma.rma", string="RMA")
    product_id = fields.Many2one('product.product',"Product", required=True)
    source_location_id =  fields.Many2one('stock.location', 'Source Location', required=True, domain=[('usage','<>','view')])
    product_qty = fields.Float('Quantity Return', required=True)
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type', help="This will determine picking type of outgoing shipment", required=True)
    des_location_id = fields.Many2one('stock.location', 'Destination', required=True, domain=[('usage','<>','view')])
    priority = fields.Selection(PROCUREMENT_PRIORITIES, 'Priority', default='1')
    is_repaired = fields.Boolean('Repaired Product Picking')


    @api.onchange('picking_type_id')
    def onchange_picking_type_id(self):
        if not self.is_repaired and self.picking_type_id:
            picktype = self.env["stock.picking.type"].browse(self.picking_type_id.id)
            if picktype.default_location_dest_id:
                self.des_location_id = picktype.default_location_dest_id.id
            if picktype.default_location_src_id:
                self.source_location_id = picktype.default_location_src_id.id

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
            'partner_id' : self.rma_id.order_id.partner_shipping_id.id,
            'priority' :self.priority,
            'location_id': self.source_location_id.id,
            'location_dest_id': self.des_location_id.id,
            'group_id' : self.rma_id.order_id.procurement_group_id.id,
        })
        x = self.env["stock.move"].create({
            'product_id': self.product_id.id,
            'product_uom_qty': float(self.product_qty),
            'name' : self.product_id.partner_ref,
            'product_uom' : self.product_id.uom_id.id,
            'picking_id': new_picking.id,
            'state': 'draft',
            'origin': self.rma_id.name,
            'location_id': self.source_location_id.id,
            'location_dest_id': self.des_location_id.id,
            'picking_type_id': pick_type_id,
            'warehouse_id': self.picking_type_id.warehouse_id.id,
            'procure_method': 'make_to_stock',
            'group_id' : self.rma_id.order_id.procurement_group_id.id,
            'partner_id':self.rma_id.order_id.partner_shipping_id.id,
        })
        new_picking.action_confirm
        new_picking.action_assign()
        self.env["rma.rma"].browse(self.rma_id.id).write({"new_do_picking_id" : new_picking.id})
        x = self.env["sale.order"].browse(self.sale_order_id.id)

        return new_picking, pick_type_id
