# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).
from odoo import fields, models


class Job(models.Model):
    _inherit = "hr.job"

    functional_area = fields.Many2many('hr.functional', string="Funtional Area", domain="[('department_id', '=', department_id)]")
    close_date = fields.Date("Close Date", help="here enter your recruitment close date")
