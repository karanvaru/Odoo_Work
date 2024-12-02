# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    config_invoice_product_id = fields.Many2one(
        'product.product',
        string="Invoice Product",
    )
