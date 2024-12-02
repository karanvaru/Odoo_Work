# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError

class RDPDx(models.Model):
    _name = "rdp.dx"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'RDP Dx'

    name = fields.Char(string='Name')