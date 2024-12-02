# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError

class FiveWhy(models.Model):
    _name = "production.calendar"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Production Calendar'

    name = fields.Char(string='Name')


