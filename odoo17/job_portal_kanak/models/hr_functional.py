# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).
from odoo import fields, models


class functionalarea(models.Model):
    _name = "hr.functional"
    _description = 'HR Functional'

    name = fields.Char('Name')
    department_id = fields.Many2one('hr.department', "Department")
