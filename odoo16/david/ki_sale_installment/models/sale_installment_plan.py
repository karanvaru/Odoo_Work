# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleInstallmentPlan(models.Model):
    _name = "sale.installment.plan"
    _description = 'Sale Installment Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,
    )
    advance = fields.Float(
        string="Advance %",
        tracking=True,
    )
    installment_number = fields.Integer(
        string='Number of Installments',
        tracking=True,
    )
    auto_post_invoice = fields.Boolean(
        string="Auto Post Invoice?",
        tracking=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Installment Product',
        required=True
    )

    @api.constrains('advance')
    def _check_advance_percentage(self):
        if self.advance < 1 or self.advance > 100:
            raise ValidationError("Advance Percentage Should Be 1 To 100 !")