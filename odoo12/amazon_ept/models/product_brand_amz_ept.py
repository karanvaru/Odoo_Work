# -*- encoding: utf-8 -*-

from odoo import models, fields


class product_brand_amz_ept(models.Model):
    _name = 'product.brand.amz.ept'
    _description = 'product.brand.amz.ept'

    name = fields.Char('Brand Name')
    description = fields.Text('Description', translate=True)
    partner_id = fields.Many2one('res.partner', string='Partner',
                                 help='Select a partner for this brand if it exists.',
                                 ondelete='restrict')
    logo = fields.Binary('Logo File')
