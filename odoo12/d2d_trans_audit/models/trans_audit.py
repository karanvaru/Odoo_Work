# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError

class TransactionAudit(models.Model):
    _name = "trans.audit"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Accounting Transactions Audit'

    name = fields.Char('Name',default=lambda self: _('New'),store=True,track_visibility='onchange')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('problem', 'Problem'),
        ('audit', 'Audited'),
        ('refuse', 'Refuse'),
    ], string='Status', default='draft',track_visibility='onchange')
    is_bill = fields.Boolean(string='Is Bill', default=False)
    is_invoice = fields.Boolean(string='Is Invoice', default=False)
    is_credit_note = fields.Boolean(string='Is Credit Note', default=False)
    is_debit_note = fields.Boolean(string='Is Debit Note', default=False)
    is_expense = fields.Boolean(string='Is Expense', default=False)
    journal = fields.Many2one('account.move', string='Journal' ,track_visibility='onchange')
    # error_type = fields.Selection([
    #     ('new_error','New Error'),
    #     ('repeated_error','Repeated Error'),
    #     ('negligible_error','Negligible Error'),
    # ], string='Type of Error',track_visibility='onchange')
    audit_remarks = fields.Html('Audit Remarks')


    @api.model
    def create(self,vals):
        vals.update({
			'name': self.env['ir.sequence'].next_by_code('trans.audit.sequence'),
		})
        return super(TransactionAudit, self).create(vals)

    @api.multi
    def action_problem(self):
        self.write({'state': 'problem'})
        return

    @api.multi
    def action_audit(self):
        self.write({'state': 'audit'})
        return

    @api.multi
    def action_refuse(self):
        self.write({'state': 'refuse'})
        return

    @api.multi
    def action_set_to_draft(self):
        self.write({'state': 'draft'})
        return