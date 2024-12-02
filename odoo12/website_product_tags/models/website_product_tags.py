# -*- coding: utf-8 -*-
#################################################################################
#
# Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# See LICENSE file for full copyright and licensing details.
#################################################################################
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'

    def _get_active_tags(self, limit=None):
        try:
            if isinstance(limit,str):
                limit = float(limit)
                limit = int(limit)
        except Exception as e:
            pass

        return self.env['wk.website.product.tags'].sudo().search([('website_publish', '=', 1)], limit=limit)

    def sale_product_domain(self):
        res = super(Website, self).sale_product_domain()
        if request.session.get("wk_product_tag_ids"):
            if len(request.session.get("wk_product_tag_ids")[2]):
                res.append(request.session.get("wk_product_tag_ids"))
        return res


class product_template(models.Model):
    _inherit = 'product.template'

    @api.one
    def _get_product_tags(self):
        product_tag_ids = self.env['wk.website.product.tags'].search([])or []
        self.product_tag_ids = map(lambda x: x.id, filter(
            lambda x: self in x.product_ids, product_tag_ids))

    @api.one
    def _set_product_tags(self):
        tags = self.env['wk.website.product.tags'].browse(
            self.product_tag_ids._ids)
        map(lambda tag: tag.write({'product_ids': [(4, self.id)]}), tags)
    product_tag_ids = fields.Many2many(
        string='Tags',
        comodel_name="wk.website.product.tags",
        relation="product_template_tags_wk_website_product_tags_relation",
        column1="product_template_tags",
        column2="wk_website_product_tags"
    )


class WkWebsiteProductTags(models.Model):

    _name = "wk.website.product.tags"

    @api.one
    def _get_product_ids(self):
        product_ids = self.env['product.template'].search([])or []
        self.product_ids = map(lambda x: x.id, filter(
            lambda x: self in x.product_tag_ids, product_ids))

    @api.one
    def _set_product_ids(self):
        products = self.env['product.template'].browse(self.product_ids._ids)
        map(lambda product: product.write(
            {'product_tag_ids': [(4, self.id)]}), products)

    name = fields.Char(string="Tag Name", required=True, translate=True)
    product_ids = fields.Many2many(
        string='Associated Product',
        comodel_name="product.template",
        relation="product_template_tags_wk_website_product_tags_relation",
        column1="wk_website_product_tags",
        column2="product_template_tags"
    )
    website_publish = fields.Boolean(
        string='Available in the website',
        default=1
    )
    website_style = fields.Text(
        string="Any Special Style",
        default="font-family: 'Opensans' Sans-serif; font-weight: 600;font-size: 18px;"
    )
    _sql_constraints = [
        ('unique_tag_name', 'unique(name)', 'Tags must be Unique .')
    ]

    @api.one
    @api.constrains('name')
    def _check_active(self):
        if len(self.search([('name', '=', self.name)])) > 1:
            raise ValidationError("Tags must be Unique !")
