# Copyright (c) 2019 Emipro Technologies Pvt Ltd (www.emiprotechnologies.com). All rights reserved.
from odoo import fields, models, api

class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    package_carrier_type = fields.Selection(selection_add=[('fedex_ept', 'Fedex')])
