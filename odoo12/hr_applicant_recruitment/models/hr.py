# -*- coding: utf-8 -*-

from openerp import api, fields, models

class Employee(models.Model):
    _inherit = "hr.employee"

    ctc = fields.Monetary(string="CTC", compute="compute_ctc")
    
    applicant_education_ids = fields.One2many(
        'applicant.education',
        'employee_id',
        string='Educations'
    )
    applicant_employeement_ids = fields.One2many(
        'applicant.employeement',
        'employee_id',
        string='Employeements'
    )
    applicant_family_ids = fields.One2many(
        'applicant.family',
        'employee_id',
        string='Familys'
    )
    applicant_medical_ids = fields.One2many(
        'applicant.medical',
        'employee_id',
        string='Medical Checkup'
    )

    def compute_ctc(self):
        for rec in self:
            contract = rec.env['hr.contract'].search([('employee_id', '=', rec.id), ('state', '=', 'open')], limit=1)
            rec.ctc = contract.x_studio_ctc
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: