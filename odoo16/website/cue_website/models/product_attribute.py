from odoo import fields, models


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    icon = fields.Binary(
        string='Icon'
    )
