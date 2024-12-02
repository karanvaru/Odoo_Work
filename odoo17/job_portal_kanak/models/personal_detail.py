# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).
from odoo import api, fields, models
from odoo.exceptions import UserError


class PersonalDetails(models.Model):
    _name = 'personal.detail'
    _description = 'Applicant Educational Information'

    personal_detail_id = fields.Many2one('hr.applicant')
    course_name = fields.Char("Course", help="here enter your Educational information")
    branch = fields.Char("Branch", help="here enter your branch/stream")
    organization = fields.Char("Organization", help="here enter your organization where you studied")
    start_date = fields.Date("Course Start Date", help="here enter your start date of your course")
    end_date = fields.Date("Course End Date", help="here enter your end date of your course")
    marks = fields.Float("Marks Obtained")

    @api.onchange('start_date', 'end_date')
    def _date_field_applicant_personal(self):
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise UserError("End date must be greater than Start date!!")
