from odoo import api, fields, models, _
from datetime import date, datetime

class LeadsButtons(models.Model):
    _inherit = 'crm.lead'

    effort = fields.Float("Effort", compute="compute_total_effort")
    activities = fields.Integer("Activities", compute="compute_total_activities")
    contract_generated = fields.Date(string="Contract Generated Date")
    delivery_to_be_completed = fields.Date(string="Delivery To Be Completed By")


    @api.multi
    def compute_total_effort(self):

        for record in self:
            for reco in record:
                c_id = reco.id
                if c_id:
                    total_effort_lines = reco.env['time.tracking.users'].search([('crm_id.id', '=', c_id)])
                    total_effort_count = reco.env['time.tracking.users'].search_count([('crm_id.id', '=', c_id)])
                if total_effort_count:
                    for rec in total_effort_lines:
                        reco['effort'] = reco['effort'] + rec['duration']

    @api.multi
    def compute_total_activities(self):

        for record in self:
            for reco in record:
                c_id = reco.id
                if c_id:
                    total_effort_count = reco.env['time.tracking.users'].search_count([('crm_id.id', '=', c_id)])
                    reco['activities'] = total_effort_count

class TimerTrackingUser(models.Model):
    _inherit = 'time.tracking.users'

    crm_id = fields.Many2one(
        'crm.lead',
        string='Crm Leads id',
    )

