# Copyright (c) 2018 Emipro Technologies Pvt Ltd (www.emiprotechnologies.com). All rights reserved.
from odoo import models, fields, api, _

class FedexStockPickingBatchEpt(models.Model):
    _inherit = "stock.picking.batch"
    delivery_type_ept = fields.Selection(selection_add=[('fedex_ept', "FedEx")])

class FedexStockPickingToBatchEpt(models.TransientModel):
    _inherit = 'stock.picking.to.batch.ept'
    delivery_type_ept = fields.Selection(selection_add=[('fedex_ept', "FedEx")])