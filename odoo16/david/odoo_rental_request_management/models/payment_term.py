# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    is_custom_rental_term = fields.Boolean(
        string='Use as Rental Default Term'
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
