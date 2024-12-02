# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountTax(models.Model):
    _inherit = "account.tax"
    
    job_invoice_line_tax = fields.Many2one(
        'job.invoice.line',
        string = "Job Invoice Line Tax"
    )
