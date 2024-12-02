from odoo import fields, models


class ProductBrandInherit(models.Model):
    _inherit = 'product.category'
    _description = 'Product Category Inherit'

    show_website = fields.Boolean(
        string="Show Website"
    )

    image = fields.Binary(
        string='Image'
    )
    brand_ids = fields.Many2many(
        'product.brand',
        string="Brands"
    )
    category_image = fields.Binary(
        string='Image'
    )
