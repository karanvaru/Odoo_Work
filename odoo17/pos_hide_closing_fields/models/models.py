# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    show_closing_financial_fields = fields.Boolean("Access To Session Closing Financial Data")



class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    show_closing_financial_fields = fields.Boolean(
        related="pos_config_id.show_closing_financial_fields", readonly=False
    )









