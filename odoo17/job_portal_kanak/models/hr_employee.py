# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).
from odoo import api, fields, models


class employeedetails(models.Model):
    _inherit = 'hr.employee'

    academic_ids = fields.One2many('employee.academic.line', 'employee_detail_id')
    certificate_ids = fields.One2many('employee.certificate.line', 'employee_certificate_id')
    profession_ids = fields.One2many('employee.professional.line', 'employee_professional_id')
    description = fields.Html("Description")

    def _create_attachment(self):
        applicant = self.env['hr.applicant'].search([('partner_id', '=', self.user_partner_id.id)], limit=1)
        vals2 = self.env['ir.attachment'].search([('res_id', '=', applicant.id)], limit=1)
        if applicant and vals2:
            for val in vals2:
                for i in self.name:
                    self.env['ir.attachment'].create({
                        'name': val.name,
                        'res_name': i,
                        'type': 'binary',
                        'datas': val.datas,
                        'res_model': 'hr.employee',
                        'res_id': self.id
                    })

    @api.model_create_multi
    def create(self, vals):
        res = super(employeedetails, self).create(vals)
        res._create_attachment()
        return res
