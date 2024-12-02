# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models, fields


class POSDayWiseReport(models.Model):
    _name = 'sh.pos.day.wise.report'
    _description = 'POS Wise Daily Report'

    name = fields.Many2one(
        comodel_name='product.product', string='Product Name')
    monday = fields.Integer(string='Monday')
    tuesday = fields.Integer(string='Tuesday')
    wednesday = fields.Integer(string='Wednesday')
    thursday = fields.Integer(string='Thursday')
    friday = fields.Integer(string='Friday')
    saturday = fields.Integer(string='Saturday')
    sunday = fields.Integer(string='Sunday')
    total = fields.Integer(string='Total')
