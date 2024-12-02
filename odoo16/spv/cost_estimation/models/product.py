# -*- coding: utf-8 -*-

from odoo import models, fields, api
import math
import re

class ProductCanBeCost(models.Model):
    _inherit = "product.template"

    cost_ok = fields.Boolean(string='Can be Cost')
    cost_estimation = fields.One2many('cost.estimation.products', 'idx')
    cost_item_type = fields.Selection([('material', 'Material'),('labour', 'Labour'),('overhead', 'Overhead'),('subcontractor', 'Subcontractor')], string="CI Type")
    estimated_cost = fields.Float(string="Estimated Cost")

    @api.model
    def create(self, vals):
        res = super(ProductCanBeCost, self).create(vals)
        ean = generate_ean(str(res.id))
        res.barcode = ean
        return res

def ean_checksum(eancode):
    if len(eancode) != 9:
        return -1
    oddsum = 0
    evensum = 0
    eanvalue = eancode
    reversevalue = eanvalue[::-1]
    finalean = reversevalue[1:]

    for i in range(len(finalean)):
        if i % 2 == 0:
            oddsum += int(finalean[i])
        else:
            evensum += int(finalean[i])
    total = (oddsum * 3) + evensum

    check = int(10 - math.ceil(total % 10.0)) % 10
    return check

def generate_ean(ean):
    if not ean:
        return "0000000000000"
    ean = re.sub("[A-Za-z]", "0", ean)
    ean = re.sub("[^0-9]", "", ean)
    ean = ean[:9]
    if len(ean) < 9:
        ean = ean + '0' * (9 - len(ean))
    return ean[:-1] + str(ean_checksum(ean))


class ProductCostEstimation(models.Model):
    _name = "cost.estimation.products"

    product_id = fields.Many2one('product.template', string='Product')
    description = fields.Text('Description')
    qty = fields.Float('Quantity')
    uom = fields.Many2one('uom.uom', string='Unit of Measure')
    # cost_item_type = fields.Selection([('material', 'Material'),('labour', 'Labour'),('overhead', 'Overhead')], string="CI Type")
    cost_item_type = fields.Selection(related='product_id.cost_item_type',string="CI Type")
    idx = fields.Many2one('product.template')
    