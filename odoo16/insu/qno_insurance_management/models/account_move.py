# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    policy_id = fields.Many2one(
        'insurance.policy',
        string='Policy',
        copy=False
    )
