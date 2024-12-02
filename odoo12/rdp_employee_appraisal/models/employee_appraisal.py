# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime



class EmployeeAppraisal(models.Model):
    _name = "employee.appraisal"
    _description = " Employee Appraisal"

    name = fields.Char('Reference', track_visibility='always', default=lambda self: _('New'))
    employee_name = fields.Many2one('res.users', string="Employee Name", required=True, default=lambda self: self.env.user, readonly=True)
    appraisal_date = fields.Datetime(string="Date", required=True)
    description = fields.Html(string='Description', required=True)
    open_day = fields.Char(string="Open Days", compute="_compute_open_days")
    priority = fields.Selection([
        ('none', 'None'),
        ('poor', 'Poor'),
        ('very_poor', 'Very Poor'),
        ('average', 'Average'),
        ('good', 'Good'),
        ('best', 'Best')
    ], string='Self Appraisal Priority', track_visibility='always')
    state = fields.Selection([
        ('draft', 'DRAFT'),
        ('closed', 'Closed'),
        ('cancel', 'CANCELLED'),
    ], string='Status', readonly=True, default='draft', track_visibility='always')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('employee.appraisal.sequence')
        res = super(EmployeeAppraisal, self).create(vals)
        return res

    @api.multi
    def action_to_closed(self):
        self.state = 'closed'

    @api.multi
    def action_to_cancel(self):
        self.state = 'cancel'

    @api.multi
    def action_set_draft(self):
        self.write({'state': 'draft'})

    @api.depends('appraisal_date')
    def _compute_open_days(self):
        for rec in self:
            if rec.appraisal_date:
                if not rec.state == 'closed':
                    print("The appraisal date is", rec.appraisal_date)
                    print("The date of today", datetime.today())
                    today = datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S")
                    date = datetime.strptime(today, "%Y-%m-%d %H:%M:%S")
                    rec.open_day = str((date - rec.appraisal_date).days + 1) + "  days"





