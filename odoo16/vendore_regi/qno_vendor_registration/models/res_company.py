# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools
import os
import base64


class ResCompany(models.Model):
    _inherit = 'res.company'

    email_background_image = fields.Binary(
        string='Email Background Image',
        attachment=True
    )

    url = fields.Char(
        string="Url",
    )

    api_url = fields.Char(
        string="API Url",
    )

    database_name = fields.Char(
        string="Database",
    )
    custom_active = fields.Boolean(
        string="Active",
        default=True,
    )
