# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError

class RDPDx(models.Model):
    _name = "rdp.presales"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'RDP Presales'

    name = fields.Char(string='Name')