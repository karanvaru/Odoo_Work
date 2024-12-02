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
import logging
_logger = logging.getLogger(__name__)


class NewMrpRepairWizard(models.TransientModel):
    _name = 'new.mrp.repair.wizard'
    _description = "New Mrp Repair Wizard"

    @api.model
    def _get_product(self):
        result = self.env['rma.rma'].browse(self._context['active_id'])
        return result.product_id

    @api.model
    def _get_product_qty(self):
        result = self.env['rma.rma'].browse(self._context['active_id'])
        return result.refund_qty

    @api.model
    def _get_partner(self):
        result = self.env['rma.rma'].browse(self._context['active_id'])
        return result.partner_id

    @api.model
    def _get_location(self):
        irmodule_obj = self.env['ir.module.module']
        vals = irmodule_obj.sudo().search([('name', 'in', ['repair']), ('state', 'in', [
            'to install', 'installed', 'to upgrade'])])
        result = self.env['rma.rma'].browse(self._context['active_id'])
        res = self.env['res.config.settings'].get_values()
        if vals:
            if res.get("repair_location_id", False) and res["repair_location_id"]:
                location_id = self.env["stock.location"].browse(res["repair_location_id"])
                return location_id
        return result.picking_id.location_dest_id

    @api.model
    def _get_destination(self):
        result = self.env['rma.rma'].browse(self._context['active_id'])
        return result.partner_id.property_stock_customer

    @api.model
    def _get_rma_id(self):
        result = self.env['rma.rma'].browse(self._context['active_id'])
        return result.id

    product_id = fields.Many2one(
        'product.product', string='Produt to Repair', readonly=True, default=_get_product)
    product_qty = fields.Float(
        'Product Quantity', readonly=True, default=_get_product_qty)
    partner_id = fields.Many2one(
        'res.partner', 'Partner', help='Choose partner for whom the order will be invoiced and delivered.', default=_get_partner)
    location_id = fields.Many2one('stock.location', 'Current Location',
                                  default=_get_location)
    location_dest_id = fields.Many2one('stock.location', 'Delivery Location',
                                       default=_get_destination)
    invoice_method = fields.Selection([
        ("none", "No Invoice"),
        ("b4repair", "Before Repair"),
        ("after_repair", "After Repair")
    ],
        default="none",  string="Invoice Method", help='Selecting \'Before Repair\' or \'After Repair\' will allow you to generate invoice before or after the repair is done respectively. \'No invoice\' means you don\'t want to generate invoice for this repair order.')
    rma_id = fields.Many2one("rma.rma", string="RMA ID", default=_get_rma_id)

    @api.multi
    def apply(self):
        self.ensure_one()
        repair_vals = {"rma_id": self.rma_id.id, 'partner_id': self.partner_id.id,
                       'product_id': self.product_id.id, 'product_qty': self.product_qty,
                       'location_id': self.location_id.id, 'location_dest_id': self.location_dest_id.id,
                       'invoice_method' : self.invoice_method,'product_uom': self.product_id.uom_id.id or False
                       }
        mrp_repair_id = self.env["repair.order"].create(repair_vals)
        rma_obj = self.env["rma.rma"].browse(self.rma_id.id)
        rma_obj.write({'mrp_repair_id' : str(mrp_repair_id.id)})
        return mrp_repair_id
