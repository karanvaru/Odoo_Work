# -*- coding: utf-8 -*-

from odoo import fields, models


class PartnerRelativeRelation(models.Model):
    _name = "partner.relative.relation"
    _description = "Customer Relative Relation"

    name = fields.Char(
        string="Relation",
        required=True,
        translate=True
    )
