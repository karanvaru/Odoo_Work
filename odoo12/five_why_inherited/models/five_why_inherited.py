from odoo import api, fields, models, _
from datetime import date,datetime

class FiveWhyInherited(models.Model):
    _inherit = 'five.why'
    _order = 'id desc'

    problem_name = fields.Char(string="Problem Name", required=True)
    problem_description = fields.Text(string="Problem Description", required=1)
    cross_functional_team_members_attended_ids = fields.Many2many('res.users', string='Cross Functional Team Members Attended')
    analysis_date = fields.Datetime(string="Analysis Date", store=True)
    analysis_started_time = fields.Datetime(string="Analysis Started Time", readonly=True)
    analysis_ended_time = fields.Datetime(string="Analysis Ended Time", readonly=True)
    chaired_by_id = fields.Many2one('res.users', string="Chaired By", required=1)
    completed_percentage = fields.Integer(string="Completed Percentage", compute="progress_bar")
    why_is_the_problem_1st_why = fields.Html(string="Why is the Problem? (1st Why?)")
    why_is_the_problem_2nd_why = fields.Html(string="Why is the Problem? (2nd Why?)")
    why_is_the_problem_3rd_why = fields.Html(string="Why is the Problem? (3rd Why?)")
    why_is_the_problem_4th_why = fields.Html(string="Why is the Problem? (4th Why?)")
    why_is_the_problem_5th_why = fields.Html(string="Why is the Problem? (5th Why?)")
    root_cause_identified = fields.Text(string="Root Cause Identified")
    action1 = fields.Char(string="Action 1")
    action2 = fields.Char(string="Action 2")
    action3 = fields.Char(string="Action 3")
    action4 = fields.Char(string="Action 4")
    action5 = fields.Char(string="Action 5")
    assigned_to_id = fields.Many2one('res.users', string="Assigned To")
    assigned_to_1_id = fields.Many2one('res.users', string="Assigned To")
    assigned_to_2_id = fields.Many2one('res.users', string="Assigned To")
    assigned_to_3_id = fields.Many2one('res.users', string="Assigned To")
    assigned_to_4_id = fields.Many2one('res.users', string="Assigned To")
    state = fields.Selection([
        ("new", "New"), ("action_in_progress", "Actions In Progress"), ("close", "Closed"), ("cancel", "Cancelled")
    ], string='Status', readonly=True, default='new', track_visibility='always')
    open_days = fields.Char(string='Open Days', compute='calculate_open_days', track_visibility='always')
    closed_date = fields.Datetime(string='Closed date')

    @api.multi
    def action_set_action_in_progress(self):
        self.state = 'action_in_progress'
        self.analysis_started_time = datetime.today()

    @api.multi
    def action_set_to_draft(self):
        self.state = 'new'

    @api.multi
    def action_set_close(self):
        self.state = 'close'
        self.analysis_ended_time = datetime.today()
        self.closed_date = datetime.today()

    @api.multi
    def action_set_cancel(self):
        self.state = 'cancel'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('five.why.sequence')
        res = super(FiveWhyInherited, self).create(vals)
        return res

    @api.depends('state')
    def progress_bar(self):
        for rec in self:
            if rec.state == "new":
                completed_percentage = 0
            elif rec.state == "action_in_progress":
                completed_percentage = 50
            elif rec.state == "close":
                completed_percentage = 100
            else:
                completed_percentage = 0
            rec.completed_percentage = completed_percentage

    @api.multi
    def calculate_open_days(self):
        for rec in self:
            if rec.closed_date:
                rec.open_days = str((rec.closed_date - rec.create_date).days) + " Days"
            else:
                rec.open_days = str((datetime.today() - rec.create_date).days) + " Days"



