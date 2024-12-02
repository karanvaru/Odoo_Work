# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _


class AdditionalFees(models.Model):
    _name = 'additional.fees.config'

    name = fields.Char(
        string='Name'
    )
    fee_type = fields.Selection(
        selection=[
            ('fixed', 'Fixed'),
            ('percentage', 'Percentage')
        ],
        string='Fee Type',
        default='percentage'
    )
    amount = fields.Float(
        string='Amount'
    )
    default_add = fields.Boolean(
        string='Default Add',
        default=False
    )
    product_id = fields.Many2one(
        'product.product',
        domain=[('type', '=', 'service')],
        string="Product"
    )


class AdditionalFeesLine(models.Model):
    _name = 'additional.fee.line'

    fee_id = fields.Many2one(
        'additional.fees.config',
        string="Fee"
    )
    amount = fields.Float(
        string='Amount'
    )
    # purchase_order_line_id = fields.Many2one(
    #     'purchase.order.line',
    #     string="Purchase Order Line"
    # )
#     purchase_order_line_wizard_id = fields.Many2one(
#         'purchase.order.line.wizard',
#         string="Purchase Order Line"
#     )
    product_id = fields.Many2one(
        'product.product',
        # domain=[('type', '=', 'service')],
        string="Product"
    )
    product_template_id = fields.Many2one(
        'product.template',
        string="Product"
    )

    # def _prepare_additional_fee_line(self):
    #     res = {
    #         'product_id': self.fee_id.product_id.id,
    #         'price_unit': self.amount,
    #     }
    #     return res


