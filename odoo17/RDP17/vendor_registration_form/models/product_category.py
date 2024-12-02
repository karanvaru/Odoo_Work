# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductCategory(models.Model):
    _inherit = 'product.category'

    custom_display_on_vendor_registration = fields.Boolean(
		string="Display on Vendor Registration"
	)
