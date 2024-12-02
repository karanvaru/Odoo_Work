# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    custom_product_category_ids = fields.Many2many(
		'product.category',
		string="Vendor Registration Categories"
	)
    custom_major_supplier_of_item = fields.Text(
		string="Major Supplier of (Name of Items)"
	)
    
