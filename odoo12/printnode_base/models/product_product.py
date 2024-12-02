# Copyright 2021 VentorTech OU
# See LICENSE file for full copyright and licensing details.

from odoo import models


class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = ['product.product', 'multi.print.mixin']
