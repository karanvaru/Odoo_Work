# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductCategory(models.Model):
    _inherit = "product.category"

    is_policy_category = fields.Boolean(
        copy=True,
        string="Is Policy Category?",
    )

    policy_type = fields.Selection(
        selection=[
            ('vehicle', 'Vehicle'),
            ('health', 'Health'),
            ('corporate', 'SME')
        ],
        string="Policy Type",
        copy=False
    )

