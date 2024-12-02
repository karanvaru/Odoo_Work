#!/usr/bin/python3
from odoo import models, fields


class PrepInstruction(models.Model):
    _name = "prep.instruction"
    _description = "Prep Instructions"

    name = fields.Char(string="Name", help="Name")
    description = fields.Char(string="Description", help="Description")
