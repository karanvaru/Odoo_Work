# -*- coding: utf-8 -*-

from odoo import fields, models


class SaleTermCondition(models.Model):
    _name = "sale.term.condition"

    name = fields.Char(
        string='Name',
        required=True,
    )
    description = fields.Html(
        string="Conditions",
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string="Customers",
        help="If customer selected then this will be available for specific customer otherwise for all"
    )
