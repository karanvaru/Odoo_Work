# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta
class FinanceProjectTask(models.Model):
    _name = "finance.project"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Finance Project & Task List'
    _order = 'id desc'

    reference = fields.Char('Reference', default=lambda self: _('New'), store=True, track_visibility='onchange')
    name = fields.Char(string='Requirement Name', required="1", track_visibility="always")
    description = fields.Text('Description', track_visibility='onchange')
    stakeholders = fields.Many2many('res.partner', string='Stakeholders', track_visibility="always")
    requirement_type = fields.Selection([
        ('department', 'Department'),
        ('bank', 'Bank'),
        ('internal', 'Internal'),
    ], string='Requirement Type', required="1", track_visibility="always")
    assigned_to = fields.Many2one('res.users', string='Assigned To', track_visibility="always", required="1")
    assigned_by = fields.Many2one('res.users', string='Assigned By', track_visibility="always", default=lambda self: self.env.user, required="1")
    start_date = fields.Date('Start Date', required="1", track_visibility="always")
    deadline_date = fields.Date('Deadline Date', required="1", track_visibility="always")
    hold_date = fields.Date(string="Hold Date", readonly=True, track_visibility="always")
    cancel_date = fields.Date(string="Cancelled Date", readonly=True, track_visibility="always")
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'P1 (Not Urgent & Non Important)'),
        ('2', 'P2 (Non Urgent & Important)'),
        ('3', 'P3 (Urgent & Non Important)'),
        ('4', 'P4 (Urgent & Important)'),
    ], string='Priority', track_visibility='onchange')
    detail_desk = fields.Html('Detailed Description', track_visibility="always")
    rating = fields.Integer(string="Rating", track_visibility="always")
    closed_date = fields.Date('Closed Date', readonly=True, track_visibility="always")
    delay_days = fields.Char('Over Due Days', compute="cal_delay_days", track_visibility="always")
    open_days = fields.Char('Open Days', compute='cal_open_days', track_visibility="always")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('wip', 'WIP'),
        ('review', 'Review'),
        ('hold', 'Hold'),
        ('close', 'Closed'),
        ('cancel', 'Cancelled')], string='Status', track_visibility='onchange', default='draft')
    planned_days = fields.Integer(string="Planned Days", compute="cal_planned_days", track_visibility="always")
    planed_days_utilization = fields.Float(string="Planed Days Utilization %", compute="cal_planed_days_utilization", track_visibility="always")
    rating = fields.Integer(string="Rating", compute="cal_rating", track_visibility="always")

    @api.model
    def create(self, vals):
        vals.update({
            'reference': self.env['ir.sequence'].next_by_code('rdp.finance.project.sequence'),
        })
        return super(FinanceProjectTask, self).create(vals)

    @api.multi
    def ff_action_wip(self):
        self.write({'state': 'wip'})
        return

    @api.one
    def ff_action_in_review(self):
        self.write({'state': 'review'})
        return

    @api.one
    def ff_action_hold(self):
        self.deadline_date = date.today()
        self.hold_date = date.today()
        self.write({'state': 'hold'})
        return

    @api.multi
    def ff_action_close(self):
        self.deadline_date = date.today()
        self.closed_date = date.today()
        self.write({'state': 'close'})
        return

    @api.multi
    def ff_action_cancel(self):
        self.deadline_date = date.today()
        self.cancel_date = date.today()
        self.write({'state': 'cancel'})
        return

    @api.one
    def ff_action_set_to_draft(self):
        self.write({'state': 'draft'})
        return

    @api.one
    def ff_action_set_to_wip(self):
        self.write({'state': 'wip'})
        return

    @api.depends('closed_date', 'cancel_date', 'hold_date', 'start_date')
    def cal_open_days(self):
        for record in self:
            current_date = date.today()
            if record.closed_date and record.start_date:
                record.open_days = record.closed_date - record.start_date
                record.open_days = str(record.open_days.split(',')[0])
                if record.open_days == '0:00:00':
                    record.open_days = '0 Days'
            elif record.hold_date:
                record.open_days = record.hold_date - record.create_date.date()
                record.open_days = str(record.open_days.split(',')[0])
                if record.open_days == '0:00:00':
                    record.open_days = '0 Days'
            elif record.cancel_date:
                record.open_days = record.cancel_date - record.create_date.date()
                record.open_days = str(record.open_days.split(',')[0])
                if record.open_days == '0:00:00':
                    record.open_days = '0 Days'
            else:
                record.open_days = current_date - record.create_date.date()
                record.open_days = str(record.open_days.split(',')[0])
                if record.open_days == '0:00:00':
                    record.open_days = '0 Days'

    @api.depends('deadline_date')
    def cal_delay_days(self):
        for record in self:
            if record.closed_date and record.deadline_date:
                record.delay_days = str((record.closed_date - record.deadline_date).days) + " Days"
                record.delay_days = record.delay_days.split(',')[0]
            elif record.deadline_date:
                record.delay_days = str((date.today() - record.deadline_date).days) + " Days"
                record.delay_days = record.delay_days.split(',')[0]
                if record.delay_days == '0:00:00':
                    record.delay_days = '0 Days'
            else:
                record.delay_days = '0 Days'

    @api.depends('start_date', 'deadline_date')
    def cal_planned_days(self):
        for record in self:
            if record.deadline_date:
                if record.deadline_date == record.start_date:
                    planed_days = 1
                    record.planned_days = planed_days + 1
                else:
                    planed_days = record.deadline_date - record.start_date
                    planed_days = str(planed_days).split(' ')[0]
                    record.planned_days = int(planed_days) + 1

    @api.depends('planned_days', 'delay_days')
    def cal_planed_days_utilization(self):
        for record in self:
            if record.planned_days:
                if record.delay_days:
                    due_days = int(record.delay_days.split(' ')[0])
                    planed_days = record.planned_days
                    record.planed_days_utilization = due_days * 100 / planed_days

    @api.depends('planed_days_utilization', 'deadline_date')
    def cal_rating(self):
        for record in self:
            pdu = record.planed_days_utilization
            if pdu >= -100 and pdu <= -76:
                record.rating = 5
            if pdu >= -75 and pdu <= -51:
                record.rating = 4
            if pdu >= -50 and pdu <= -76:
                record.rating = 3
            if pdu >= -25 and pdu <= 0:
                record.rating = 2
            if pdu >= 1 and pdu <= 10:
                record.rating = 1
            if pdu >= 11 and pdu <= 25:
                record.rating = 0
            if pdu >= 26 and pdu <= 50 :
                record.rating = -1
            if pdu >= 51 and pdu <= 75:
                record.rating = -2
            if pdu >=76  and pdu <=100 :
                record.rating = -3
            if pdu >= 101 and pdu <= 150:
                record.rating = -4
            if pdu >= 151 and pdu <= 200:
                record.rating = -5
            if pdu >= 201:
                record.rating = -6

