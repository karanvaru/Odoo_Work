# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ContractInherit(models.Model):
    _inherit = 'hr.contract'

    commission_amount = fields.Float(
        string="Commission Amount"
    )
    commission_currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.user.company_id.currency_id.id
    )
