# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AnalyticLine(models.Model):
    _inherit = "account.analytic.line"
    
    invoiced_created = fields.Boolean(
        string="Invoiced",
        copy=False,
    )
    time_in = fields.Float(
        string='Time In',
    )
    time_out = fields.Float(
        string='Time Out',
    )
    custom_timesheet_invoice_id = fields.Many2one(
        'account.move',
        string='Ticket Timesheet Invoice',
        copy=False,
    )
