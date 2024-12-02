# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResCountry(models.Model):
    _inherit = 'res.country'

    country_manager_id = fields.Many2one(
        'res.users',
        string="Manager"
    )

class ResCountryGroup(models.Model):
    _inherit = 'res.country.group'

    country_group_manager_id = fields.Many2one(
        'res.users',
        string="Manager"
    )
