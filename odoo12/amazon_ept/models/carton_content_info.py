from odoo import models, fields, api


class carton_content_info(models.Model):
    _name = "amazon.carton.content.info.ept"
    _description = 'amazon.carton.content.info.ept'

    @api.one
    def get_products(self):
        product_ids = []
        for amazon_product in self.package_id.amazon_product_ids:
            product_ids.append(amazon_product.id)
            # product_ids.append(line.amazon_product_id.id)
        self.amazon_product_ids = product_ids

    amazon_product_ids = fields.One2many("amazon.product.ept", compute="get_products",
                                         string="Amazon Products")
    amazon_product_id = fields.Many2one("amazon.product.ept", string="Amazon Product")
    seller_sku = fields.Char(size=120, string='Seller SKU', related="amazon_product_id.seller_sku",
                             readonly=True)
    quantity = fields.Float("Carton Qty", digits=(16, 2))
    package_id = fields.Many2one("stock.quant.package", string="Package")

    @api.onchange('package_id')
    def on_change_product_id(self):
        product_ids = []
        if self.package_id:
            if isinstance(self.package_id, int):
                product_ids = self.package_id.amazon_product_ids.ids
            else:
                product_ids = self.package_id._record.amazon_product_ids.ids
        return {'domain': {'amazon_product_id': [('id', 'in', product_ids)]}}
