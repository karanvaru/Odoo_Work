# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models
from odoo.tools.translate import _  
    
class Applicant(models.Model):
    _inherit = "hr.applicant"
    
    job_history_id = fields.Many2one('hr.job.history', 'Job History')
    
class RecruitmentSource(models.Model):
    _inherit = "hr.recruitment.source"

    job_history_id = fields.Many2one('hr.job.history', "Job Histroy ID")
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: