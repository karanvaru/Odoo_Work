# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models, fields


class MotorcycleMake(models.Model):
    _name = "motorcycle.make"
    _description = 'make model'
    _order = 'id desc'

    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id.id
    )
