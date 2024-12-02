# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_dealer = fields.Boolean(
        string="is Dealer",
        copy=False
    )
