# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class AccountPaymentInherit(models.Model):
    _inherit = "account.payment"

    flipkart_payment_settlement_id = fields.Many2one(
        comodel_name="flipkart.payment.settlement",
        string="Flipkart Payment Settlement",
    )
