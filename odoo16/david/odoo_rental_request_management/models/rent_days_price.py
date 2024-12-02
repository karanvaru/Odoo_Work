# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class CustomRentDayPrice(models.Model):
    _name="custom.rent.day.price"
    _description = 'Rent Day Price Configuration'

    product_tmpl_id = fields.Many2one(
        'product.template',
        string="Product Template",
    )
    days_from = fields.Float(
        string="Days From",
        required=True,
    )
    days_to = fields.Float(
        string="Days To",
        required=True,
    )
    price = fields.Float(
        string="Rental Price",
        required=True,
    )
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        default=lambda self: self.env.company.currency_id.id,
        required=True
    )
    pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Pricelist'
    )
    product_variant_ids = fields.Many2many(
        'product.product',
        string='Product Variants',
        store=True,
    )

    @api.onchange('pricelist_id')
    def _onchange_pricelist_id(self):
        for pricing in self.filtered('pricelist_id'):
            pricing.currency_id = pricing.pricelist_id.currency_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
