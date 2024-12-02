# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_custom_rental_published = fields.Boolean(
        string='Is Rental Published',
        copy=False,
    )
    custom_rental_product = fields.Boolean(
        string='Is Rental Product',
        default=False,
    )
    custom_rent_day_ids = fields.One2many(
        'custom.rent.day.price',
        'product_tmpl_id',
        string="Rent Day Price",
    )

    def action_view_rental_so_line_report(self):
        action = self.env.ref("odoo_rental_request_management.action_rental_so_line_reservations").sudo().read()[0]
        if self.custom_rental_product:
            action['domain'] = [('product_id', 'in', self.product_variant_ids.ids)]
        return action


class Product(models.Model):
    _inherit = 'product.product'

    custom_rental_qty = fields.Float(
        string='Rental Quantity',
    )

    def action_view_rental_so_line_report(self):
        action = self.env.ref("odoo_rental_request_management.action_rental_so_line_reservations").sudo().read()[0]
        if self.product_tmpl_id.custom_rental_product:
            action['domain'] = [('product_id', 'in', self.ids)]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
