# Copyright 2021 VentorTech OU
# See LICENSE file for full copyright and licensing details.

from odoo import models


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = ['product.template', 'multi.print.mixin']

    def _add_multi_print_lines(self):
        products = self.mapped('product_variant_ids')
        return super(ProductTemplate, self)._add_multi_print_lines(records=products)
