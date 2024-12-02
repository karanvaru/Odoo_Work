# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import fields, models


class MotorcycleGarage(models.Model):
    _name = "motorcycle.garage"
    _description = "Motorcycle Garage"
    _order = "id desc"

    name = fields.Char(
        string="Name",
        compute="_compute_complete_name"
    )
    year_id = fields.Integer(
        string="Start year"
    )

    mmodel_id = fields.Many2one(
        comodel_name="motorcycle.mmodel",
        string="Model",
        # required=True
    )
    type_id = fields.Many2one(
        comodel_name="motorcycle.type",
        string="Type",  # related="mmodel_id.type_id",
        store=True
    )
    make_id = fields.Many2one(
        comodel_name="motorcycle.make",
        string="Make",
        # related="mmodel_id.make_id",
        store=True
    )

    user_id = fields.Many2one(comodel_name="res.users",
                              string="User",
                              required=True)

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id.id
    )

    def _compute_complete_name(self):
        if self:
            for rec in self:
                name = ''
                if rec.type_id:
                    name += rec.type_id.name + ' '
                if rec.make_id:
                    name += rec.make_id.name + ' '
                if rec.mmodel_id:
                    name += rec.mmodel_id.name + ' '
                if rec.year_id:
                    name += str(rec.year_id) + ' '
                if name == '':
                    name = False
                rec.name = name
