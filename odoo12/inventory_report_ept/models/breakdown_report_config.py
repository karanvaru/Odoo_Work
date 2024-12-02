from odoo import models, fields, api, _
from odoo.exceptions import  UserError, ValidationError


class BreakdownReportConfig(models.Model):
    
    _name = "breakdown.report.config.ept"
    
    _rec_name = "company_id"
    
    day_start = fields.Integer('Day Start', required=True, default=1)
    day_end = fields.Integer('Day End', requird=True, default=1)     
    company_id = fields.Many2one('res.company', 'Company')
    
    @api.multi
    @api.constrains('day_start', 'day_end')
    def _check_days(self):
        for record in self:
            if record.day_start >= record.day_end:
                raise ValidationError(_('Start day Should be Smaller than End day!'))
              
            if record.day_start <= 0 or record.day_end <= 0:
                raise ValidationError(_('Please enter positive values for days.'))   
                
            
