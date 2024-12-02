from odoo import api, fields, models


class ProductGroup(models.Model):
    _name = 'product.group'
    _description = 'product Group'

    name = fields.Char(string="Product Group", required=True)
