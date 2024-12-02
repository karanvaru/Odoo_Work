# -*- coding: utf-8 -*-
#################################################################################
#
# Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# See LICENSE file for full copyright and licensing details.
#################################################################################
import werkzeug
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging
_logger = logging.getLogger(__name__)


class WebsiteSale(WebsiteSale):

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        response= super(WebsiteSale, self).shop(page, category, search,ppg,**post)
        Tag = request.env['wk.website.product.tags']
        IrDefault =  request.env['ir.default'].sudo()
        product_tags_limit =IrDefault.get('website.product.tags.setting', 'product_tags_limit')
        response.qcontext['product_tags'] =request.website._get_active_tags(limit=product_tags_limit)
        wk_product_tag_ids = request.session.get('wk_product_tag_ids')
        if wk_product_tag_ids:
            wk_product_tag_ids = wk_product_tag_ids[2]
            response.qcontext['wk_tags_list'] = Tag.sudo().browse(wk_product_tag_ids)
        return response

    @http.route(['/product/tags/remove/<tag_id>'], type='http', auth="public",  website=True)
    def product_tags_remove(self, tag_id):
        if request.session.get('wk_product_tag_ids'):
            request.session.get('wk_product_tag_ids')[2].remove(int(tag_id))
        request.session['wk_product_tag_ids'] = request.session.get('wk_product_tag_ids')
        return request.redirect(request.httprequest.referrer or '/shop')

    @http.route(['/product/tags/<tag_id>'], type='http', auth="public",  website=True)
    def product_tags_add(self, tag_id):
        tag_id = int(tag_id)
        if request.session.get('wk_product_tag_ids'):
            if tag_id not in request.session['wk_product_tag_ids'][2]:
                request.session['wk_product_tag_ids'][2].append(tag_id)
        else:
            request.session['wk_product_tag_ids'] = (
                'product_tag_ids', 'in', [tag_id])
        request.session['wk_product_tag_ids'] = request.session.get(
            'wk_product_tag_ids')
        return request.redirect(request.httprequest.referrer or '/shop')
