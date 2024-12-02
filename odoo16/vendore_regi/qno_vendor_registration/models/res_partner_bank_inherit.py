# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    upload_bank_cheque = fields.Binary(
        string='Bank Cheque'
    )
    upload_bank_cheque_name = fields.Char(
        string='Bank Cheque'
    )

class ResBank(models.Model):
    _inherit = 'res.bank'
    
    
    bank_code = fields.Char(
        string="Bank Code",
    )
