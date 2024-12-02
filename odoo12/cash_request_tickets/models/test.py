# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date, datetime



class CashRequestTickets(models.Model):
    _name = "cash.request.tickets"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "cash request tickets"

    # student_update_id = fields.One2many('create.application', 'student_details_ids')
    # name = fields.Char("Names", readonly=True)
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    office_location_id = fields.Many2one('x_work_office', string="Office Location", track_visibility='always')
    created_by = fields.Char(string="Requested By", track_visibility='always')

    subject = fields.Char(string="Subject", track_visibility='always')
    employee_name = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user, readonly='1')
    # description = fields.Text(string='Description', required=True, copy=False, readonly=True, index=True, default=lambda self : _('New'))
    notes = fields.Text(string='Notes')
    description = fields.Text(string="Description", required=True)
    amount = fields.Integer(string='Amount')
    bank_details = fields.Text(string="Bank Details")
    journal_id = fields.Many2one('account.journal', string="Journal", required=True)
    partner_id = fields.Many2one('res.partner', String="Partner", compute='compute_partner_name')
    qty =fields.Integer(string="Quantity", default=1, readonly=True)
    state = fields.Selection([
        ('draft', 'DRAFT'),
        ('bill_submit', 'BILL SUBMIT'),
        ('paid', 'PAID'),
        ('closed', 'Closed'),
        ('cancel', 'CANCELLED'),
    ], string='Status', readonly=True, default='draft', track_visibility='always')
    open_days = fields.Char('Open Days', compute='calculate_open_days')
    closed_date = fields.Datetime('Closed Date')
    hr_expense_id = fields.Many2one('hr.expense', "HR Expense")
    cr_count_id = fields.Integer('cash count', compute="cash_request_count")
    account_payment_id = fields.Many2one('account.payment', "Payment")
    cash_request_count_id = fields.Integer('cash request count', compute="cash_request_tickets_count")
    employee_id=fields.Many2one('hr.employee', string='Employee Name', compute='compute_employee_name')
    @api.multi
    def cash_request_count(self):
        count_values = self.env['hr.expense'].search_count([('cash_request_id','=',self.id)])
        self.cr_count_id = count_values

    @api.multi
    def cash_request_tickets_count(self):
        count_values = self.env['account.payment'].search_count([('tickets_id', '=', self.id)])
        self.cash_request_count_id = count_values

    @api.multi
    def calculate_open_days(self):
        for rec in self:
            if rec.closed_date:
                rec.open_days = (rec.closed_date - rec.create_date).days
            else:
                rec.open_days = (datetime.today() - rec.create_date).days

    # def create(self, vals):
    #     if vals.get('reference_seq', _('New')) == _('New'):
    #         vals['reference_seq'] = self.env['ir.sequence'].next_by_code('template.four.sequence') or _('New')
    #     result = super(TemplateFour, self).create(vals)
    #     return result
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('cash.request.sequence')
        res = super(CashRequestTickets, self).create(vals)
        return res

    # @api.multi
    # def action_to_expense(self,vals):
    #
    #     hr_expense_details = self.env['hr.expense']

    @api.multi
    def action_to_expense(self, vals):
        hr_expense_details = self.env['hr.expense']

        # in product_id =3030 for main
        vals = {
            'cash_request_id':self.id,
            'product_id': 3030,
            'unit_amount': self.amount,
            'quantity': 1.000,
            'date': datetime.today(),
            'employee_id': self.employee_id.id,
            'x_studio_bank_details':self.description,
            'name': self.subject,
            'payment_mode': 'own_account',
        }
        new_val = hr_expense_details.create(vals)
        self.state = 'bill_submit'
        return new_val

    @api.multi
    def open_cash_ticket(self):
        self.ensure_one()
        return {
            'name': 'Cash Request',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'hr.expense',
            'domain': [('cash_request_id','=',self.id)],

        }

    @api.multi
    def action_to_payment(self, vals):
        payment_details = self.env['account.payment']
        # in product_id =3030 for main
        vals = {
            'tickets_id':self.id,
            'payment_date':datetime.today(),
            'partner_id':  self.partner_id.id,
            # 'journal_id':  self.journal_id.id ,
            'journal_id': self.journal_id.id or None,
            'payment_type': 'outbound',
            'payment_method_id': 1,
            'amount':self.amount,
            'account_id': 14,
            # 'x_studio_is_related_to':'',
        }
        new_val = payment_details.sudo().create(vals)
        self.state = 'paid'
        return new_val

    @api.multi
    def cash_ticket_open(self):
        self.ensure_one()
        return {
            'name': 'Payment',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'domain': [('tickets_id', '=', self.id)],
        }
    @api.depends('employee_name')
    def compute_employee_name(self):
        for rec in self:
            print("==========The current user id =================================", rec.env.uid)
            rec_employee_id = rec.env['hr.employee'].sudo().search([('user_id', '=', rec.employee_name.id)])
            rec.employee_id = rec_employee_id.id
            print(" =================The current user id ========================", rec.employee_id)

    @api.depends('employee_name')
    def compute_partner_name(self):
        for rec in self:
            user = rec.env['res.users'].search([('id', '=', rec.employee_name.id)])
            rec.partner_id = user.partner_id






    @api.multi
    def action_to_work_in_progress(self):
        self.state = 'work_in_progress'

    # @api.multi
    # def action_to_paid(self):
    #     self.state = 'paid'


    @api.multi
    def action_to_bill_submit(self):
        self.state = 'bill_submit'

    @api.multi
    def action_to_close(self):
        self.state = 'closed'

    @api.multi
    def action_to_cancel(self):
        self.state = 'cancel'

    @api.multi
    def action_set_draft(self):
        self.write({'state': 'draft'})

class CashRequestManyToOneRelation(models.Model):
    _name = "cash.request.many.to.one.relation"

    _description = "Many To Many"

    name = fields.Char('Name')

class HRExpensesValues(models.Model):
    _inherit = "hr.expense"

    cash_request_id = fields.Many2one('cash.request.tickets', string="Cash Request Id")

class AccountPayment(models.Model):
    _inherit = "account.payment"

    tickets_id = fields.Many2one('cash.request.tickets', string="Tickets Id")




