# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).
from odoo import api, fields, models
from odoo.exceptions import UserError


class EmployeeCertificate(models.Model):
    _name = 'employee.certificate.line'
    _description = 'Employee Certificate Information'

    employee_certificate_id = fields.Many2one('hr.employee')
    course_name = fields.Char("Course", help="here enter your Educational information")
    branch = fields.Char("Branch", help="here enter your branch/stream")
    organization = fields.Char("Organization", help="here enter your organization where you studied")
    certificate_des = fields.Char("Description of Certificate")
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    start_date = fields.Date("Course Start Date", help="here enter your start date of your course")
    end_date = fields.Date("Course End Date", help="here enter your end date of your course")

    @api.onchange('start_date', 'end_date')
    def _date_field_onchange_certificate(self):
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise UserError("End date must be greater than Start date!!")
