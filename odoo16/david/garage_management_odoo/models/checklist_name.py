# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ChecklistName(models.Model):
    _name = "quality.checklist.name"
    _description = 'Quality Checklist'

    name = fields.Char(
        string = "Name"
    )