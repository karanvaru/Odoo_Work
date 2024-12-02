# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    generate_commission = fields.Boolean(
        string="Generate Commission?",
        default=False
    )
    level_no = fields.Integer(
        string="Level Limit",
        default=0
    )
    commission_level_ids = fields.One2many(
        'commission.level.config',
        'company_id',
        string="Level Configuration",
    )
    commission_product_id = fields.Many2one(
        'product.product',
        string="Commission Product",
    )
    commission_based_on = fields.Selection([
        ('sale', 'Sale'),
        ('point_of_sale', 'Point Of Sale'),
    ], string="Commission Based On", default='sale')

    def actin_compute_levels(self):
        self.ensure_one()
        self.commission_level_ids.unlink()
        lines = []
        for level in range(1, self.level_no+1):
            lines.append((0, 0, {
                'level_no': level,
                'percentage': 0.0
            }))
        self.sudo().write({'commission_level_ids' : lines})
