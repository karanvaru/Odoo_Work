# -*- coding: utf-8 -*-

from num2words import num2words
from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words" )

    @api.depends('amount_total')
    def amount_to_words(self):
        if self.company_id.text_amount_language_currency:
            self.text_amount = num2words(self.amount_total, to='currency',
                                         lang=self.company_id.text_amount_language_currency)