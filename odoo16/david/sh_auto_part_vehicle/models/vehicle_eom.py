# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models, fields


class ShVehicleOEM(models.Model):
    _name = "sh.vehicle.oem"
    _description = "Vehicle OEM"

    name = fields.Char('Code', required=True)
    supplier_id = fields.Many2one('res.partner', string="Supplier")
    is_visible_website = fields.Boolean('Is visible on website?')
    product_id = fields.Many2one('product.template', string='Product')


class ShProductSpecification(models.Model):
    _name = "sh.product.specification"
    _description = "Product Specification"

    name = fields.Char('Label', required=True)
    value = fields.Char('Value')
    product_id = fields.Many2one('product.template', string='Product')
