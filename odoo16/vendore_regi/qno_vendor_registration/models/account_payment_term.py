# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    sap_code = fields.Char(
        string="SAP Code",
    )
