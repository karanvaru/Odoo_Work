# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError

class FinanceAudit(models.Model):
    _name = "finance.audit"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Finance Audit'
    _order = 'id desc'

    name = fields.Char('Reference',default=lambda self: _('New'),store=True,track_visibility='onchange')
    partner_id = fields.Many2one('res.partner',string="Partner", required="1", track_visibility='always')
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.user.company_id.currency_id)
    statement_start_date = fields.Date(string="Statement Start Date", track_visibility='always')
    statement_end_date = fields.Date(string="Statement End Date", track_visibility='always')
    audit_by = fields.Many2one('res.partner',string="	Audit By", required="1", track_visibility='always')
    ba_rdp_closing_amount = fields.Monetary(string="BA RDP Closing Amount",currency_field='currency_id', track_visibility='always')
    ba_partner_closing_amount = fields.Monetary(string="BA Partner Closing Amount",currency_field='currency_id', track_visibility='always')
    ba_differ_amount = fields.Monetary(string="BA Differ Amount",currency_field='currency_id', compute="compute_ba_differ_amount", track_visibility='always')
    aa_rdp_closing_amount = fields.Monetary(string="AA RDP Closing Amount",currency_field='currency_id', track_visibility='always')
    aa_partner_closing_amount = fields.Monetary(string="AA Partner Closing Amount",currency_field='currency_id', track_visibility='always')
    aa_differ_amount = fields.Monetary(string="AA Differ Amount",currency_field='currency_id', compute="compute_aa_differ_amount", track_visibility='always')
    state = fields.Selection([("draft","Draft"),("request_statement","Request Statement"),("statement_received","Statement Received"),("in_progress","In Progress"),("close","Closed"),("cancel","Cancelled")], string='Status', default='draft', track_visibility='always')
    audit_remarks = fields.Html(string="Audit Remarks")
    financial_year_id = fields.Many2one('financial.year', string="Financial Year", required="1")
    
    @api.model
    def create(self, vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code('finance.audit.sequence'),
        })
        return super(FinanceAudit, self).create(vals)
    
    @api.multi
    def action_set_draft(self):
        self.write({'state': 'draft'})
    
    @api.multi
    def action_request_statement(self):
        self.write({'state': 'request_statement'})
    
    @api.multi
    def action_to_statement_received(self):
        self.write({'state': 'statement_received'})
    
    @api.multi
    def action_to_in_progress(self):
        self.state = 'in_progress'
    
    @api.multi
    def action_to_close(self):
        self.state = 'close'
    
    @api.multi
    def action_to_cancel(self):
        self.state = 'cancel'

    @api.depends('ba_rdp_closing_amount','ba_partner_closing_amount')
    def compute_ba_differ_amount(self):
        for rec in self:
            rec.ba_differ_amount = rec.ba_rdp_closing_amount - rec.ba_partner_closing_amount
    
    @api.depends('aa_rdp_closing_amount', 'aa_partner_closing_amount')
    def compute_aa_differ_amount(self):
        for rec in self:
            rec.aa_differ_amount = rec.aa_rdp_closing_amount - rec.aa_partner_closing_amount
        
class  FinancialYear(models.Model):
    _name = 'financial.year'
    _description = "Financial Year"
    
    name = fields.Char(string="Name")