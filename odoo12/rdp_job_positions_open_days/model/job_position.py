from odoo import models, fields, api
from datetime import datetime, date


class StudentDetails(models.Model):
    _inherit = 'hr.job'

    open_days = fields.Char(compute='_compute_open_days', string='Open Days')
    date = fields.Date(string='Date', default=fields.Date.today)

    @api.depends('create_date')
    def _compute_open_days(self):
        for rec in self:
            if rec.create_date:
                if not rec.state == 'open':
                    print("The create_date date is", rec.create_date)
                    print("The date of today", datetime.today())
                    today = datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S")
                    date = datetime.strptime(today, "%Y-%m-%d %H:%M:%S")
                    rec.open_days = str((date - rec.create_date).days + 1) + "  days"
            else:
                rec.open_days = (datetime.today() - rec.create_date).days
