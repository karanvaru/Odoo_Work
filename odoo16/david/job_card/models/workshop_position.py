# -*- coding: utf-8 -*-

from odoo import fields, models


class WorkshopPosition(models.Model):
    _name = "workshop.position"
    _description = "Workshop Position"

    name = fields.Char(
        string="Name",
        required=True,
    )
    team_ids = fields.Many2many(
        'hr.employee',
        string='Team Members',
    )
