# -*- coding: utf-8 -*-
from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    transaction_type_id = fields.Many2one(
        'journal.entry.type',
        string="JE Type",
        track_visibility="onchange",
        copy=False
    )
