# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models, api


# Product Template
class ProductTemplateBranch(models.Model):
    _inherit = 'product.template'

    branch_id = fields.Many2one(
        'res.branch', string="Branch", default=lambda self: self.env.user.branch_id)


class ProductSupplierinfoBranch(models.Model):
    _inherit = 'product.supplierinfo'

    branch_id = fields.Many2one(
        'res.branch', string="Branch", default=lambda self: self.env.user.branch_id)


class ProductPricelistBranch(models.Model):
    _inherit = 'product.pricelist'

    branch_id = fields.Many2one(
        'res.branch', string="Branch")


class ProductPricelistItemBranch(models.Model):
    _inherit = 'product.pricelist.item'

    branch_id = fields.Many2one(
        'res.branch', 'Branch',
        readonly=True, related='pricelist_id.branch_id', store=True)
