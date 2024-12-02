# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    sap_code = fields.Char(
        string="SAP Code",
    )

