from odoo import fields, models


class ProductTagInherits(models.Model):
    _inherit = 'product.tag'
    _description = 'Product Tags'

    product_tag_categ_id = fields.Many2one(
        'product.tag.category',
        string='Product Category Tags'
    )

