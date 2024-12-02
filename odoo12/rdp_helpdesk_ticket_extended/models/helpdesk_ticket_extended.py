from odoo import fields, models, api
from odoo.exceptions import UserError
from datetime import datetime

class HelpdDeskExtended(models.Model):
    _inherit = "helpdesk.ticket"

    last_updated_before = fields.Char(string="Last Updated Before", compute="compute_last_updated_before")
    activity_count = fields.Integer('Activity Count', compute="compute_total_effort_count")
    total_effort = fields.Float('Total Effort', compute="compute_total_effort")
    city_category_id = fields.Many2one('helpdesk.ticket.city',string ="City Category",track_visibility="onchange")
    def compute_last_updated_before(self):
        for rec in self:
            if rec.write_date:
                rec.last_updated_before = str((datetime.today()-rec.write_date).days) + " Days Ago"


    @api.depends('team_id')
    def compute_total_effort(self):
        for record in self:
            for reco in record:
                h_id = reco.id
                if h_id:
                    total_effort_lines = reco.env['time.tracking.users'].search([('helpdesk_id.id', '=', h_id)])
                    total_effort_count = reco.env['time.tracking.users'].search_count([('helpdesk_id.id', '=', h_id)])
                    if total_effort_count:
                        for rec in total_effort_lines:
                            reco['total_effort'] = reco['total_effort'] + rec['duration']

    @api.depends('activity_count')
    def compute_total_effort_count(self):
        for record in self:
            h_id = self.id
            total_effort_count = self.env['time.tracking.users'].search_count([('helpdesk_id.id', '=', h_id)])
            if total_effort_count:
                record['activity_count'] = total_effort_count

class HelpdDeskCityCategory(models.Model):
    _name = "helpdesk.ticket.city" 
    _description ="Helpdesk City Category"    


    name = fields.Char('Name')           




