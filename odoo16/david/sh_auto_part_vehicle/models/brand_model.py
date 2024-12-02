# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import fields, models


class MotorcycleBrand(models.Model):
    _name = "motorcycle.brand"
    _description = "Motorcycle Brand"
    _order = "sequence"

    name = fields.Char(required=True)
    sequence = fields.Integer(
        string=" "
    )
