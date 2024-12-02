from odoo import models, fields, models, api, _
from datetime import date, datetime

class ComplainceRequest(models.Model):
    _name = 'complaince.request'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Complaince and it is notices."

    reference_no = fields.Char(string='Sequence Number',
                               readonly=True, default='New', required=True)
    name = fields.Char(string='Name')
    document_number = fields.Integer(string='Document Number', track_visibility='always')
    assigned_to_id = fields.Many2one('hr.employee', string='Assigned To', track_visibility='always')
    date = fields.Date(string='Date', track_visibility='always')
    hearing_date = fields.Date(string='Hearing Date', track_visibility='always')
    stake_holders_ids = fields.Many2many('res.partner', string='Stakeholders', track_visibility='always')
    type_id = fields.Many2one('type.id', string='Type', track_visibility='always')
    subject = fields.Char(string='Subject', track_visibility='always')
    detail_description = fields.Html(string='Detail Description', track_visibility='always')
    department_id = fields.Many2one('hr.department', string='Department', track_visibility='always')
    state = fields.Selection([
        ('draft', 'DRAFT'),
        ('wip', 'WIP'),
        ('hold', 'HOLD'),
        ('resolved', 'RESOLVED'),
        ('cancelled', 'CANCELLED'),
    ], string='Status', default='draft', track_visibility='always')
    open_days = fields.Char(string='Open Days', compute='calculate_open_days',track_visibility='always')
    closed_date = fields.Datetime(string='closed date', track_visibility='always')



    @api.multi
    def action_set_to_draft(self):
        self.write({'state':'draft'})

    @api.multi
    def action_to_wip(self):
        self.state = 'wip'

    @api.multi
    def action_to_hold(self):
        self.state = 'hold'

    @api.multi
    def action_to_resolved(self):
        self.state = 'resolved'

    @api.multi
    def action_to_cancelled(self):
        self.state = 'cancelled'

    @api.multi
    def calculate_open_days(self):
        for rec in self:
            if rec.closed_date:
                rec.open_days = (rec.closed_date - rec.create_date).days
            else:
                rec.open_days = (datetime.today() - rec.create_date).days

class TypeId(models.Model):
    _name = 'type.id'
    _description = 'Type Field'

    name = fields.Char(string='Name')






