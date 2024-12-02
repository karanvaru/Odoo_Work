# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################

from odoo import fields, models, api, _
from datetime import datetime


class res_partner(models.Model):
    _inherit = 'res.partner'

    vendor_product_ids = fields.One2many(comodel_name="product.supplierinfo", inverse_name='partner_id', string="Product Pricelist")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: