# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import api, fields, models
from odoo.exceptions import UserError


class EmployeeProfessional(models.Model):
    _name = 'employee.professional.line'
    _description = 'Employee Profession Information'

    employee_professional_id = fields.Many2one('hr.employee')
    name = fields.Char("name", help="here enter your Educational information")
    organization = fields.Char("Organization", help="Where you worked")
    department = fields.Char("Department", help="here enter your Department")
    start_date = fields.Date("working Start Date", help="here enter your start date")
    end_date = fields.Date("working End Date", help="here enter your end date")
    work_exp = fields.Char("Work Experience")
    work_des = fields.Char("Work Description")
    projects = fields.Char("Project", help="if you have done any solo project describe here")

    @api.onchange('start_date', 'end_date')
    def _date_field_onchange(self):
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise UserError("End date must be greater than Start date!!")
