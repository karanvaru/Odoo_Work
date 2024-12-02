# -*- coding: utf-8 -*-
from odoo import fields, models, api


class FeesAccountMapping(models.Model):
    _name = "fees.account.mapping"

    field_ids = fields.Many2many(
        comodel_name="ir.model.fields",
        string="Charges Type",
        domain="[('model', '=', 'flipkart.payment.settlement')]"
    )
    account_id = fields.Many2one(
        comodel_name="account.account",
        string="Account",
    )
    post_type = fields.Selection([
        ('credit', 'Credit'),
        ('debit', 'Debit')
    ],
        string="Post Type",
        copy=False
    )

    refund_post_type = fields.Selection([
        ('credit', 'Credit'),
        ('debit', 'Debit')
    ],
        string="Refund Post Type",
        copy=False
    )

    sale_shop_id = fields.Many2one(
        comodel_name="sale.shop",
        string="Sale Shop",
    )



