from odoo import api, fields, models,_


class ProductTemplateInt(models.Model):
    _inherit = "product.template"

    shop_product_count = fields.Integer(compute='compute_count')



    def compute_count(self):
        for record in self:
            record.shop_product_count = self.env['sale.shop.product'].search_count(
                    [('product_tmpl_id', '=', record.id)])

    def shop_product_templated(self):
        self.ensure_one()
        act = self.env.ref('mtrmp_sales_shop.actions_sale_product_shop_view').read([])[0]
        act['domain'] = [('product_tmpl_id', '=', self.id)]
        return act


class ProductProduct(models.Model):
    _inherit = "product.product"

    shop_product_product_count = fields.Integer(compute='compute_count')
    _sql_constraints = [
        ('default_code_unique', 'unique(default_code)', "A Master SKU can only be assigned to one "
                                                     "Product !"),
    ]

    def compute_count(self):
        for record in self:
            record.shop_product_product_count = self.env['sale.shop.product'].search_count(
                [('product_id', '=', record.id)])

    def shop_product_product(self):
        self.ensure_one()
        act = self.env.ref('mtrmp_sales_shop.actions_sale_product_shop_view').read([])[0]
        act['domain'] = [('product_id', '=', self.id)]
        return act