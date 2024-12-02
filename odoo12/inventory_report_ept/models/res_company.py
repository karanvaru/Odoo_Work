from odoo import models, fields, api, _
from odoo.exceptions import  UserError, ValidationError

class ResCompany(models.Model):
    _inherit = "res.company"
    
    avg_sales_days = fields.Integer(string='Average Sales', default=1)
    breakdown_line_ids = fields.One2many('breakdown.report.config.ept', 'company_id', 'Days Breakdown')
    
     
    @api.multi
    @api.constrains('breakdown_line_ids')
    def _check_days(self):
        if self.breakdown_line_ids:
            end_day_lst = []
            start_day_lst = []
            for line in self.breakdown_line_ids:
                start_day_lst.append(line.day_start)
                end_day_lst.append(line.day_end + 1)
                
                self.env.cr.execute('''SELECT id FROM breakdown_report_config_ept WHERE (day_start <= %s and %s <= day_end) AND id <> %s and company_id=%s''', (line.day_end, line.day_start, line.id,line.company_id.id))
                if any(self.env.cr.fetchall()):
                    raise ValidationError(_('You cannot have 2 Breakdown lines that overlap!'))
                
            start_day_lst.pop(0)
            for start_day in start_day_lst:
                if start_day not in end_day_lst:
                    raise ValidationError(_('Breakdown phases are not in sequence! Please maintain continuous breakdown sequence.'))




