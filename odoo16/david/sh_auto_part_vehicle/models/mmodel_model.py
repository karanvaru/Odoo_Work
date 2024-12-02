# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models, fields


class MotorcycleMmodel(models.Model):
    _name = "motorcycle.mmodel"
    _description = "mmodel"
    _order = "id desc"

    name = fields.Char(string="Name", required=True)
    make_id = fields.Many2one(
        comodel_name="motorcycle.make",
        string="Make", required=True
    )
    type_id = fields.Many2one(
        comodel_name="motorcycle.type",
        string="Type", required=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id.id
    )
