# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class Account(models.Model):
    _inherit = 'account.account'

    is_stock_account = fields.Boolean(string="Stock Account?", copy=False)

    dashboard_sequence = fields.Integer(
        string='Dashboard Sequence',
    )

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_stock_journal = fields.Boolean(string="Stock Account?", copy=False)

