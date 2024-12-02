# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models, fields


class MotorcycleType(models.Model):
    _name = "motorcycle.type"
    _description = "type model"
    _order = "id desc"

    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id.id
    )
