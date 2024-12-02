from odoo import api, fields, models, _
from datetime import date, datetime
import time

class FmTicket(models.Model):
    _name = "fm.ticket"


    date = fields.Date(string="Date")
    employee_name = fields.Many2one('res.users', string="Employee Name", default=lambda self: self.env.user, readonly=True)
    concern = fields.Html(string="Request")
    assigned_to = fields.Many2one('hr.employee', string="Assigned To", compute="compute_assigned_to", readonly=False)
    name = fields.Char(string='FM Reference No', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    open_days = fields.Char(string='Open Days', compute='calculate_open_days')
    closed_date = fields.Datetime(string='closed date')
    state = fields.Selection([
        ('new', 'NEW'),
        ('close', 'CLOSE'),
        ('cancel', 'CANCEL'),
    ], string='Status', default='new', track_visibility='always',)

    @api.model
    def create(self, vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code('fm.sequence'),
        })

        return super(FmTicket, self).create(vals)

    @api.multi
    def action_to_close(self):
        self.closed_date = datetime.today()
        self.state = 'close'

    @api.multi
    def action_to_cancel(self):
        self.closed_date = datetime.today()
        self.state = 'cancel'

    @api.multi
    def action_set_new(self):
        self.write({'state': 'new'})

    @api.multi
    def calculate_open_days(self):
        for rec in self:
            if rec.closed_date:
                rec.open_days = (rec.closed_date - rec.create_date).days
            else:
                rec.open_days = (datetime.today() - rec.create_date).days
    @api.depends('date')
    def compute_assigned_to(self):
        print("The assigned to function")
        users_id = []
        for rec in self:
            print("It is coming inside ")
            assign = rec.env['hr.employee'].search([('job_id.name', '=', 'Facility Manager')])
            print("The assign to is comming for the ids",assign)
            rec.assigned_to = assign
            print("The help team is assigned to ", rec.assigned_to)

                # rec.write({'assigned_to': users_id})


