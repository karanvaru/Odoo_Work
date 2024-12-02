# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import fields, models


class MotorcycleTransmission(models.Model):
    _name = "motorcycle.transmission"
    _description = "Motorcycle Transmission"
    _order = "sequence"

    name = fields.Char(required=True)
    sequence = fields.Integer(
        string=" "
    )
