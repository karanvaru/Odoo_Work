from odoo import api, fields, models, _


class RepairTimeDashboard(models.Model):
    _inherit = 'repair.order'

    effort = fields.Float('Effort',compute="compute_total_effort")
    activities = fields.Integer('Activities',compute="compute_total_activities")

    @api.multi
    def compute_total_effort(self):
        
        for record in self:
            for reco in record:
                r_id = reco.id
                if r_id:
                    total_effort_lines = reco.env['time.tracking.users'].search([('repair_id.id','=',r_id)])
                    total_effort_count = reco.env['time.tracking.users'].search_count([('repair_id.id','=',r_id)])
                if total_effort_count==1:
                    for rec in total_effort_lines:
                        reco['effort'] = reco['effort'] + rec['duration']
    @api.multi
    def compute_total_activities(self):
        
        for record in self:
            for reco in record:
                r_id = reco.id
                if r_id:
                    total_effort_count = reco.env['time.tracking.users'].search_count([('repair_id.id','=',r_id)])
                    reco['activities'] = total_effort_count