# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class ProductViewSpecificationWizard(models.TransientModel):
    _name = 'product.view.specification.wizard'
    _description = 'Product View Specification Wizard'

    product_specification_ids = fields.Many2many(
        'sh.product.specification',
        string="Product Specification",
        readonly=True
    )

    @api.model
    def default_get(self, fields):
        rec = super(ProductViewSpecificationWizard, self).default_get(fields)
        active_id = self._context.get('active_id')
        active_browse_id = self.env['sale.order.line'].browse(active_id)
        product_specification_lst = []
        for res in active_browse_id.product_id.specification_lines:
            product_specification_lst.append(res.id)
        rec.update({
            'product_specification_ids': [(6, 0, product_specification_lst)],
        })
        return rec
