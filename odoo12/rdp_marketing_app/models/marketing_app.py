# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date, datetime



class MarketingApp(models.Model):
    _name = "marketing.app"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Marketing App"

    # student_update_id = fields.One2many('create.application', 'student_details_ids')

    name = fields.Char(string='Reference No', required=True, copy=False,track_visibility='always', readonly=True, index=True, default=lambda self : _('New'))
    to_do = fields.Char(string="To Do", track_visibility='always')
    # date = fields.Date(string="Date", track_visibility='always')
    req_description = fields.Text(string="Description")
    stake_holders = fields.Many2many('res.partner', string="Stake holders", track_visibility='onchange')
    requirement_type = fields.Selection([
        ('marketing', 'Marketing'),
        ('branding', 'Branding'),
        ('New Feature', 'Task'),
        ('project ', 'Project'),
        ('other', 'Other'),
    ], string='Requirement Type', track_visibility='always', required="True")
    department = fields.Many2one('hr.department', 'Department',track_visibility='always')
    assigned_by = fields.Many2one('res.users', 'Assigned By', track_visibility='always')
    assigned_to = fields.Many2one('res.users', 'Assigned To', track_visibility='always')
    start_date = fields.Datetime('Start Date', track_visibility='always')
    deadline_date = fields.Datetime('Deadline Date', track_visibility='always')
    # reference_seq = fields.Char(string='Reference No', required=True, copy=False, readonly=True, index=True, default=lambda self : _('New'))
    open_days = fields.Char(string='Open Days', compute='calculate_open_days')
    closed_date = fields.Datetime(string='closed date')
    tag_ids = fields.Many2many('marketing.tags', 'marketing_tags_rel', 'name', string='Tags', track_visibility='always')
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High'),
    ], string='Priority', track_visibility='always')
    state = fields.Selection([
        ('new', 'New'),
        ('work_in_progress', 'WIP'),
        ('hold', 'HOLD'),
        ('live', 'LIVE'),
        ('closed', 'CLOSED'),
        ('cancel', 'CANCELLED'),
    ], string='Status', readonly=True, default='new', track_visibility='always')
    completed_percentage = fields.Integer('Completed Percentage', readonly='1', compute="progress_bar", track_visibility='always')
    description = fields.Html("Description")
    delay_days = fields.Char(string="Delay Days", readonly="1", store="1", compute="cal_delay_days")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('marketing.sequence')
        res = super(MarketingApp, self).create(vals)
        template_id = self.env['ir.model.data'].get_object_reference('rdp_marketing_app', 'marketing_app_create_email_template')[1]
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(res.id, force_send=True)
        return res


    @api.multi
    def action_to_work_in_progress(self):
        self.state = 'work_in_progress'

    @api.multi
    def action_to_live(self):
        self.state = 'live'
        template_id = self.env['ir.model.data'].get_object_reference('rdp_marketing_app', 'marketing_app_closing_update_email_template')[1]
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)

    @api.multi
    def action_to_hold(self):
        self.deadline_date = datetime.today()
        self.closed_date = datetime.today()
        self.state = 'hold'

    @api.multi
    def action_to_closed(self):
        self.deadline_date = datetime.today()
        self.closed_date = datetime.today()
        self.state = 'closed'

    @api.multi
    def action_to_cancel(self):
        self.deadline_date = datetime.today()
        self.closed_date = datetime.today()
        self.state = 'cancel'

    @api.multi
    def action_set_draft(self):
        self.write({'state': 'new'})

    @api.multi
    def calculate_open_days(self):
        for rec in self:
            if rec.closed_date:
                rec.open_days = (rec.closed_date - rec.create_date).days
            else:
                rec.open_days = (datetime.today() - rec.create_date).days

    @api.depends('state')
    def progress_bar(self):
        for rec in self:
            # if rec.state != "hold":
            if rec.state == "new":
                completed_percentage = 0
            elif rec.state == "work_in_progress":
                completed_percentage = 30
            elif rec.state == "live":
                completed_percentage = 60
            elif rec.state == "closed":
                completed_percentage = 100
            else:
                completed_percentage = 0
            rec.completed_percentage = completed_percentage

    @api.depends('deadline_date')
    def cal_delay_days(self):
        for record in self:
            if record.deadline_date:
                record.delay_days = str((datetime.today() - record.deadline_date).days) + " Days"
                record.delay_days = record.delay_days.split(',')[0]
                if record.delay_days == '0:00:00':
                    record.delay_days = '0 Days'
            else:
                record.delay_days = '0 Days'

            if record.closed_date and record.deadline_date:
                record.delay_days = str((record.closed_date - record.deadline_date).days) + " Days"
                record.delay_days = record.delay_days.split(',')[0]


class MarketingAppTags(models.Model):
    _name = "marketing.tags"

    _description = "Marketing App Tags"

    name = fields.Char('Name')



