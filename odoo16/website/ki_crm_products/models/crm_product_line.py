# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class CrmProductLine(models.Model):
    _name = 'crm.product.line'
    _description = 'Crm Product Line'

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True
    )
    crm_lead_id = fields.Many2one(
        'crm.lead',
    )
    quantity = fields.Float(
        string='Quantity',
        required=True,
        default=1
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit Of Measure',
        required=True
    )
    price_unit = fields.Float(
        string='Unit Price',
        required=True
    )
    sub_total = fields.Float(
        string='Subtotal',
        required=True,
        compute="compute_sub_total"
    )

    @api.model
    @api.depends('price_unit', 'quantity')
    def compute_sub_total(self):
        for rec in self:
            rec.sub_total = rec.price_unit * rec.quantity

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            if rec.product_id:
                rec.uom_id = rec.product_id.uom_id
