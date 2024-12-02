# -*- coding: utf-8 -*-

from odoo import models, fields


class Task(models.Model):
    _inherit = 'project.task'

    resolution = fields.Html(
        string="Resolution",
    )
