# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models, api

# Account
class AccountMoveBranch(models.Model):
    _inherit = 'account.move'

    branch_id = fields.Many2one(
        'res.branch', string="Branch", default=lambda self: self.env.user.branch_id)


class AccountMoveLineBranch(models.Model):
    _inherit = 'account.move.line'

    branch_id = fields.Many2one(related="move_id.branch_id",
                                string="Branch", store=True)


class AccountPaymentBranch(models.Model):
    _inherit = 'account.payment'

    branch_id = fields.Many2one(
        'res.branch', string="Branch", default=lambda self: self.env.user.branch_id)

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:

            account_move = self.env['account.move'].search(
                [('name', '=', vals.get('ref'))], limit=1)

            if account_move and account_move.branch_id:
                vals.update({'branch_id': account_move.branch_id.id})

            payments = super(AccountPaymentBranch, self).create(vals_list)

        return payments


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    branch_id = fields.Many2one(
        'res.branch', string="Branch")

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", move.branch_id as branch_id"

class AccountTax(models.Model):
    _inherit = 'account.tax'

    branch_id = fields.Many2one(
        'res.branch', string="Branch", default=lambda self: self.env.user.branch_id)

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    branch_id = fields.Many2one(
        'res.branch', string="Branch", default=lambda self: self.env.user.branch_id)

class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    branch_id = fields.Many2one(
        'res.branch', string="Branch", )

class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    branch_id = fields.Many2one(
        'res.branch', string="Branch", default=lambda self: self.env.user.branch_id)