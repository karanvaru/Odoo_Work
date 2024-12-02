# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    date_to = fields.Date(
        string='Date',
        related="slip_id.date_to",
        store=True
    )
    payslip_name =  fields.Char(
        string='Payslip Name',
        related="slip_id.name",
        store=True
    )

