# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class Account(models.Model):
    _inherit = 'account.account'

    is_stock_account = fields.Boolean(string="Stock Account?")

