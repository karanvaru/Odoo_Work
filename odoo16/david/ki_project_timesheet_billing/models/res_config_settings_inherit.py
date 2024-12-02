# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResConfigSettingsInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    config_invoice_product_id = fields.Many2one(
        'product.product',
        string="Invoice Product",
        related='company_id.config_invoice_product_id',
        store=True,
        readonly=False
    )

