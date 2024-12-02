# -*- coding: utf-8 -*-

from odoo import models, fields

class TypeOfSubject(models.Model):
    _name = 'type.of.subject'
    _description = "Type of Subject"
    
    name = fields.Char(
        'Name',
        required=True,
    )
