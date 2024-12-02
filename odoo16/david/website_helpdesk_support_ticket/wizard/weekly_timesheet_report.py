# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.exceptions import Warning
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class WeeklyTimesheetReport(models.TransientModel):
    _name = 'weekly.timesheetreport'
    
    today = fields.Datetime.from_string(fields.Datetime.now())
    year, week, dow = today.isocalendar()
    if dow == 7:
        start_date = today
    else:
        start_date = today - timedelta(dow)

    end_date = start_date + timedelta(6)

    start_date = fields.Date(
        'Start Date',
        required = True,
        default=start_date,
    )
    end_date = fields.Date(
        'End Date',
        required = True,
        default=end_date,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required = True,
    )
    
#    @api.multi odoo13
    def weekly_time_sheet_report(self):
        start_date = datetime.date(datetime.strptime(self.start_date, "%Y-%m-%d"))
        end_date = datetime.date(datetime.strptime(self.end_date, "%Y-%m-%d"))
        
        diff = end_date - start_date
        if diff.days > 6:
            raise UserError(_('Please Select Correct Date For one week'))
            
        data = self.sudo().read()[0]
        return self.env['report'].get_action(self, 'website_helpdesk_support_ticket.report_weekly', data = data)
        
        
