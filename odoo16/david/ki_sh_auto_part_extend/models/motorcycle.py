# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class MotorcycleMotorcycle(models.Model):
    _inherit = "motorcycle.motorcycle"

    product_count = fields.Float(
        string="Product Count",
        compute="_compute_product_count"
    )
    year_id = fields.Many2one(required=False)
    end_year_id = fields.Many2one(required=False)

    def _compute_product_count(self):
        for rec in self:
            count = self.env['product.product'].search_count([('id', 'in', rec.product_ids.ids)])
            rec.product_count = count

    def action_product(self):
        act_read = self.env.ref('product.product_normal_action_sell').sudo().read([])[0]
        act_read['domain'] = [('id', 'in', self.product_ids.ids)]
        act_read['context'] = {}
        return act_read


class ShVehicleOem(models.Model):
    _inherit = "sh.vehicle.oem"

    product_product_id = fields.Many2one(
        'product.product',
        string="Product"
    )


class ShProductSpecification(models.Model):
    _inherit = "sh.product.specification"

    product_product_id = fields.Many2one(
        'product.product',
        string="Product"
    )
