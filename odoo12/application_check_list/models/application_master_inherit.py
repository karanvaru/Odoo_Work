
from odoo import models, fields, api


class AplicationMasterInherit(models.Model):
    _inherit = 'hr.applicant'

    @api.depends('application_checklist')
    def application_progress(self):
        for each in self:
            total_len = self.env['application.checklist'].search_count([])
            entry_len = len(each.application_checklist)
            if total_len != 0:
                each.application = (entry_len * 100) / total_len

    application_checklist = fields.Many2many('application.checklist', 'app_obj', 'app_hr_rel', 'hr_app_rel',
                                      string='Application Process',
                                      domain=[('document_type', '=', 'exit')])
    exit_progress = fields.Float(compute=application_progress, string='Application Progress', store=True, default=0.0)
    maximum_rate = fields.Integer(default=100)
    check_list_enable = fields.Boolean(invisible=True, copy=False)

class AplicationChecklistInherit(models.Model):
    _inherit = 'application.checklist'


    app_obj = fields.Many2many('hr.applicant', 'application_progress', 'hr_app_rel', 'app_hr_rel',
                                invisible=1)
