# -*- coding: utf-8 -*-
from odoo import fields, models


class BlueDartService(models.Model):
    _name = 'bluedart.service'
    _description = 'BlueDart Service'

    name = fields.Char('Service Name', required=True, index=True, help="Name of service")
    product_code = fields.Char('Product Code', required=True, help="Product Code")
    product_sub_code = fields.Char('Sub Product Code')
    package_type = fields.Char('Package Type')
