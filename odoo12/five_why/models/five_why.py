# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError

class FiveWhy(models.Model):
    _name = "five.why"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = '5Why'

    name = fields.Char(string='Name')
    


