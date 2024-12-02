# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    record_type_id = fields.Many2one(
        'record.type',
        string="Record Type",
        track_visibility="onchange",
        copy=False
    )

    record_category_id = fields.Many2one(
        'record.category',
        string = "Record Category",
        track_visibility = "onchange",
        copy = False
    )

