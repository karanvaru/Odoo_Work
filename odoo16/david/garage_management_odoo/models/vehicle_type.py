# -*- coding: utf-8 -*-

from odoo import fields, models

class VehicleType(models.Model):
    _name = "vehicle.type.custom"
    _description = "Vehicle Type"

    name = fields.Char(
        string="Name",
        required=True,
    )