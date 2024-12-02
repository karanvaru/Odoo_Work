# -*- coding: utf-8 -*-

from odoo import models, fields

class TicketType(models.Model):
    _name = 'ticket.type'
    _description = "Ticket Type"
    
    name = fields.Char(
        'Name',
        required=True,
    )
