from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
import time

class RdpDx(models.Model):
    _inherit = 'rdp.dx'

    requirement_name = fields.Char(string="Requirement Name")
    description = fields.Text(string="Description", track_visibility='always')
    stake_holders = fields.Many2many('res.partner', string="Stake holders", track_visibility='always')
    requirement_type = fields.Selection([
        ('bug', 'Bug(Some Functional/Technical,which stops the operation)'),
        ('changes', 'Support(Changes Small/Big Add/Remove)'),
        ('new_feature', 'Task(Improvements/Requirements From Team)'),
        ('new_app', 'New App'),
        ('other', 'Other'),
    ], string='Requirement Type')
    department = fields.Many2one('hr.department', 'Department', track_visibility='always')
    development_by = fields.Many2one('res.partner', 'Development By', track_visibility='always')
    # assigned_by = fields.Many2one('res.users', 'Assigned By', track_visibility='always')

    assigned_to = fields.Many2one('res.users', 'Assigned To', track_visibility='always')
    start_date = fields.Date('Start Date', track_visibility='always')
    deadline_date = fields.Date('Deadline Date', track_visibility='always')
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High'),
    ], string="Priority")
    completed_percentage = fields.Integer('Completed Percentage', readonly='1', compute="progress_bar", track_visibility='always')


    concept_description = fields.Html('Concept Description', track_visibility='always')
    workflow_description = fields.Html('Workflow Description', track_visibility='always')
    drama_description = fields.Html('Drama Description', track_visibility='always')
    estimated_cost = fields.Monetary('Estimated Cost', track_visibility='always')
    cost_per_hour = fields.Monetary('Cost Per/Hour', track_visibility='always')

    dx_description = fields.Char("Description", track_visibility='always')

    estimated_time = fields.Integer('Estimated Time(Hours)', track_visibility='always')
    currency_id = fields.Many2one('res.currency', 'Currency', track_visibility='always')

    open_days = fields.Char(string="Open Days", readonly="1", compute="cal_open_days")
    closed_date = fields.Date("Closed Date")
    delay_days = fields.Char(string="Delay Days", readonly="1", compute="cal_delay_days")

    ecoc = fields.Boolean('eCOC(Word, PPT, Sheet)', track_visibility='always')
    all_views = fields.Boolean('All Views (List, Pivot, Kanban, etc..)', track_visibility='always')
    all_key_fields = fields.Boolean('All KEY fields in Group By & Filter', track_visibility='always')
    app_check_list = fields.Many2many('check.list', string='App Check List', track_visibility='always')
    responsible_by = fields.Many2one('responsible.by', 'Responsible By')
    state = fields.Selection([
        ('draft', 'DRAFT'),
        ('front_desk', 'FRONT DESK'),
        ('assigned', 'ASSIGNED'),
        ('wip', 'WIP'),
        ('testing', 'TESTING'),
        ('submit_to_admin', 'Submit To Admin'),
        ('live', 'LIVE'),
        ('documentation', 'Documentation'),
        ('hold', 'Hold'),
        ('closed', 'CLOSED'),
        ('cancel', 'CANCELLED')
    ], string='Status', default='draft', track_visibility='always', )

    @api.model
    def create(self, vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code('dx.sequence')
        })

        return super(RdpDx, self).create(vals)



    @api.multi
    def action_to_wip(self):
        self.state = 'wip'

    @api.multi
    def action_to_front_desk(self):
        self.state = 'front_desk'

    @api.multi
    def action_to_assigned(self):
        self.state = 'assigned'

    @api.multi
    def action_to_testing(self):
        self.state = 'testing'

    @api.multi
    def action_to_submit_to_admin(self):
        self.state = 'submit_to_admin'

    @api.multi
    def action_to_live(self):
        self.deadline_date = date.today()
        self.closed_date = date.today()
        self.state = 'live'

    @api.multi
    def action_to_documentation(self):
        self.state = 'documentation'

    @api.multi
    def action_to_hold(self):
        self.deadline_date = date.today()
        self.closed_date = date.today()
        self.state = 'hold'

    @api.multi
    def action_to_close(self):
        self.deadline_date = date.today()
        self.closed_date = date.today()
        self.state = 'closed'

    @api.multi
    def action_to_cancel(self):
        self.deadline_date = date.today()
        self.closed_date = date.today()
        self.state = 'cancel'

    @api.multi
    def action_set_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_set_work_in_progress(self):
        self.write({'state': 'wip'})

    @api.depends('state')
    def progress_bar(self):
        for rec in self:
            # if rec.state != "hold":
            if rec.state == "draft":
                completed_percentage = 0
            elif rec.state == "front_desk":
                completed_percentage = 15
            elif rec.state == "assigned":
                completed_percentage = 30
            elif rec.state == "wip":
                completed_percentage = 45
            elif rec.state == "testing":
                completed_percentage = 60
            elif rec.state == "submit_to_admin":
                completed_percentage = 75
            elif rec.state == "live":
                completed_percentage = 90
            elif rec.state == "documentation":
                completed_percentage = 95
            elif rec.state == "closed":
                completed_percentage = 100
            else:
                completed_percentage = 0
            rec.completed_percentage = completed_percentage

    @api.depends('closed_date')
    def cal_open_days(self):
        for record in self:
            created_date = record.create_date
            created_date_now = created_date.date()
            if record.closed_date:
                record.open_days = str((record.closed_date - created_date_now).days) + " Days"
            else:
                record.open_days = str((date.today() - created_date_now).days) + " Days"

            record.open_days = record.open_days.split(',')[0]
            if record.open_days == '0:00:00':
                record.open_days = '0 Days'


    @api.depends('deadline_date')
    def cal_delay_days(self):
        for record in self:
            if record.deadline_date:
                record.delay_days = str((date.today() - record.deadline_date).days) + " Days"
                record.delay_days = record.delay_days.split(',')[0]
                if record.delay_days == '0:00:00':
                    record.delay_days = '0 Days'
            else:
                record.delay_days = '0 Days'

            if record.closed_date and record.deadline_date:
                record.delay_days = str((record.closed_date - record.deadline_date).days) + " Days"
                record.delay_days = record.delay_days.split(',')[0]
    effort = fields.Float("Effort", compute="compute_total_effort")
    activities = fields.Integer("Activities", compute="compute_total_activities")

    @api.multi
    def compute_total_effort(self):

        for record in self:
            for reco in record:
                d_id = reco.id
                if d_id:
                    total_effort_lines = reco.env['time.tracking.users'].search([('dx_id.id', '=', d_id)])
                    total_effort_count = reco.env['time.tracking.users'].search_count([('dx_id.id', '=', d_id)])
                if total_effort_count:
                    for rec in total_effort_lines:
                        reco['effort'] = reco['effort'] + rec['duration']

    @api.multi
    def compute_total_activities(self):

        for record in self:
            for reco in record:
                d_id = reco.id
                if d_id:
                    total_effort_count = reco.env['time.tracking.users'].search_count([('dx_id.id', '=', d_id)])
                    reco['activities'] = total_effort_count


class TimerTrackingUser(models.Model):
    _inherit = 'time.tracking.users'

    dx_id = fields.Many2one(
        'rdp.dx',
        string='Dx id',
    )

class CheckList(models.Model):
    _name = "check.list"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Check List"

    name = fields.Char("Checklist")
    description = fields.Char("Description", track_visibility='always')

class ResponsibleBy(models.Model):
    _name = "responsible.by"
    _description = "Responsible By"

    name = fields.Char("Responsible By")
