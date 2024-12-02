# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date

class WeeklyTimeSheetReport(models.AbstractModel):
    _name = 'report.website_helpdesk_support_ticket.report_weekly'
    
    @api.model
    def render_html(self, docids, data=None):
        
        active_ids = data['context'].get('active_ids')
        weekly_timesheet_wizard_obj = self.env['weekly.timesheetreport']
        weekly_timesheet_wizard_ids = weekly_timesheet_wizard_obj.browse(active_ids)
        hr_timesheet_obj = self.env['hr_timesheet_sheet.sheet']
        user_ids =  []
        
        start_date = datetime.date(datetime.strptime(weekly_timesheet_wizard_ids.start_date, "%Y-%m-%d"))
        end_date = datetime.date(datetime.strptime(weekly_timesheet_wizard_ids.end_date, "%Y-%m-%d"))
        
        employee = weekly_timesheet_wizard_ids.employee_id
        timesheets = hr_timesheet_obj.search([('employee_id', '=', employee.id)])

        total_td = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        time_sheet_line = {}
        timesheets_line_ids = timesheets.timesheet_ids
        
        for line in timesheets_line_ids:
            date = datetime.date(datetime.strptime(line.date, "%Y-%m-%d"))
            if date >= start_date and date <= end_date:
                date = date.weekday()
                project_id = line.project_id
                hour = line.unit_amount
                hour_list = total_td[date]
                total_td[date] = hour_list + hour 
                
                if project_id not in time_sheet_line:
                    hour_amount = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]
                    hour_amount_list = hour_amount[date]
                    hour_amount[date] = hour_amount_list + hour
                    time_sheet_line.update({project_id : hour_amount})
                else:
                    unit_amount = time_sheet_line[project_id]
                    unit_amount[date] = unit_amount[date] + hour
                    time_sheet_line[project_id] = unit_amount

        
        total_td.append(sum(total_td))
                
        if data.get(weekly_timesheet_wizard_ids,False):
            user_ids = [weekly_timesheet_wizard_ids][0]
        else:
            user_ids = docids


        docs = weekly_timesheet_wizard_ids
        
        docargs = {
            'doc_ids': user_ids,
            'doc_model': 'weekly.timesheetreport',
            'timesheet_lines' : time_sheet_line,
            'td_total' : total_td,
            'data': data,
            'docs': docs,
        }
        return self.env['report'].render('website_helpdesk_support_ticket.report_weekly', docargs)
        
