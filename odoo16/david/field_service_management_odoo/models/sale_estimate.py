# -*- coding: utf-8 -*-

from odoo import models, fields

class SaleEstimate(models.Model):
    _inherit = 'sale.estimate'
   
    custom_field_service = fields.Many2one(
        'project.task',
        string='Field Service',
    )