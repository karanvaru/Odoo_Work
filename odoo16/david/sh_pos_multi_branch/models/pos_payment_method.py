# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models

class PosPaymentMethodBranch(models.Model):
    _inherit = 'pos.payment.method'

    branch_id = fields.Many2one(
        'res.branch', string="Branch", default=lambda self: self.env.user.branch_id)
