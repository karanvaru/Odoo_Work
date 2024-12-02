# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    additional_fee_ids = fields.One2many(
        'additional.fee.line',
        'product_template_id',
        string="Additional Fee"
    )
    total_cost = fields.Monetary(
        string="Total Cost",
        compute='_compute_total_cost'
    )

    @api.onchange('additional_fee_ids')
    def set_final_value(self):
        total = 0
        for rec in self.additional_fee_ids:
            total += rec.amount
        self.standard_price = total

    @api.depends('additional_fee_ids')
    def _compute_total_cost(self):
        total = 0
        for rec in self.additional_fee_ids:
            total += rec.amount
        self.total_cost = total


class ProductProduct(models.Model):
    _inherit = 'product.product'

    additional_fee_ids = fields.One2many(
        'additional.fee.line',
        'product_id',
        string="Additional Fee",
    )
    total_cost = fields.Monetary(
        string="Total Cost",
        compute='_compute_total_cost',
    )

    @api.onchange('additional_fee_ids')
    def set_final_value(self):
        total = 0
        for rec in self.additional_fee_ids:
            total += rec.amount
        self.standard_price = total

    @api.depends('additional_fee_ids')
    def _compute_total_cost(self):
        total = 0
        for rec in self.additional_fee_ids:
            total += rec.amount
        self.total_cost = total
