# -*- coding: utf-8 -*-
from odoo import api, fields, models


class EmployeeAcademic(models.Model):
    _inherit = 'employee.academic.line'

    marks = fields.Char("Marks Obtained")

