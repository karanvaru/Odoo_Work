from odoo import models, fields,api
from datetime import datetime


class EmployeeInherited(models.Model):
    _inherit = 'source.eng'
    _order = 'id desc'

    se_category_id = fields.Many2one('se.category.source.eng', string="SE Category")
    goal_date = fields.Date(string='Goal Date')
    companies_id = fields.Many2one('res.company',string='Companies',required=True)
    notes = fields.Text(string='Notes')
    internal_notes = fields.Text(string='Notes')
    goal_date_status = fields.Selection([('achieved','Achieved'), ('delayed','Delayed'),])
    completed_percentage = fields.Integer(string="Completed Percentage", compute="progress_bar")
    open_days = fields.Char(string="Open Days", compute="compute_open_days")
    delayed_reason = fields.Text(string="Delayed Reason")
    state = fields.Selection([
        ('new', 'NEW'),
        ('wip', 'WIP'),
        ('hold', 'Hold'),
        ('Closed', 'CLOSED'),
        ('Cancel', 'Cancelled'),

    ], string='Status', default='new')
    # state = fields.Selection([('new','NEW'), ('wip','WIP'),('hold','HOLD'),('closed','CLOSED'),('cancel','CANCEL')])

    @api.depends('create_date')
    def compute_open_days(self):
        for rec in self:
            rec.open_days = datetime.today() - rec.create_date
            rec.open_days = rec.open_days.split(',')[0]

    @api.depends('state')
    def progress_bar(self):
        for rec in self:
            if rec.state == "new":
                completed_percentage = 0
            elif rec.state == "wip":
                completed_percentage = 50
            elif rec.state == "Close":
                completed_percentage = 100
            else:
                completed_percentage = 0
            rec.completed_percentage = completed_percentage

    @api.multi
    def action_set_new(self):
        self.write({'state': 'new'})

    @api.multi
    def action_to_wip(self):
        self.state = 'wip'

    @api.multi
    def action_set_hold(self):
        self.state = 'hold'

    @api.multi
    def action_set_closed(self):
        self.state = 'Closed'

    @api.multi
    def action_to_cancel(self):
        self.state = "Cancel"


class SECategory(models.Model):
    _name = 'se.category.source.eng'
    _description = "Source Engineering"

    name = fields.Char(string="Name")


