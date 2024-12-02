# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    company_manager_id = fields.Many2one(
        'res.users',
        string="Manager"
    )
    company_ceo_id = fields.Many2one(
        'res.users',
        string="CEO"
    )
