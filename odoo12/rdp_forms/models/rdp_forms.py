# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError

class RDPForms(models.Model):
    _name = "rdp.forms"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'RDP Forms'

    name = fields.Char(string='Name')