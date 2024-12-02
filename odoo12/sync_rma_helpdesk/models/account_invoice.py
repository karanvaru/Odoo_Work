# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket', copy=False, readonly=True)
