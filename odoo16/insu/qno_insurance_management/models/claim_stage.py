# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Stage(models.Model):
    _name = "insurance.claim.details.stage"
    _description = "Insurance Claim Details Stages"

    name = fields.Char(
        string='Stage Name',
        required=True,
        translate=True
    )
    sequence = fields.Integer(
        string='Sequence',
        default=1,
        help="Used to order stages. Lower is better."
    )
    default_stage = fields.Boolean(
        copy=True,
        string="Default Stage",
    )
