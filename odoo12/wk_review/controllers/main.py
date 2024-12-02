# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

import re
import werkzeug
from odoo import http
from odoo.http import request
from odoo.tools.translate import _
from odoo import api
from werkzeug import url_encode
import base64
import odoo
from odoo import SUPERUSER_ID
from odoo import http
from odoo.exceptions import AccessError

from odoo.addons.web.controllers.main import binary_content

import logging
_logger = logging.getLogger(__name__)

class review(http.Controller):

    @http.route(['/shop/review/<string:redirect>'], type='http', auth="public", methods=['POST'], website=True, csrf = False)
    def review(self, redirect=False, **post):
        if request.env.user._is_public():
            url = "/shop/product/"+redirect+'#write-review'
            return werkzeug.utils.redirect("/web/login?redirect="+werkzeug.url_quote_plus(url))
        if post.get('review') and post.get('contact_name') and post.get('email') and post.get('title'):
            if post.get('stars'):
                review_array = {}
                review_array['msg'] = post.get('review')
                review_array['stars'] = post.get('stars')
                review_array['contact_name'] = post.get('contact_name')
                review_array['email'] = post.get('email')
                review_array['title'] = post.get('title')
                review_obj = request.env['website']._product_review(review_array, post.get('product_tmp_id'))
                config_setting_obj = request.env['website.review.config'].sudo().get_values()
                return werkzeug.utils.redirect(request.httprequest.referrer + "#write-review?%s" % url_encode({'auto_publish': config_setting_obj["auto_publish"], 'message': config_setting_obj["message_when_unpublish"]}))

    @http.route(['/shop/review/vote'], type='json', auth="public", methods=['POST'], website=True)
    def review_vote(self,  review_id, vote=0,  **post):
        if request.env.user._is_public():
            return False
        like_dislike_obj = request.env['review.like.dislike']
        res = []
        if not review_id:
            return False
        if vote == 0:
            return False
        if review_id and vote:
            like_dislike_ids = request.env['review.like.dislike'].search(
                [('review_id', '=', review_id), ('customer_id', '=', request.uid)])
            if like_dislike_ids:
                vote_id = like_dislike_obj.browse(like_dislike_ids[0])
                if vote == 1:
                    like_dislike_ids[0].write({"like": True, "dislike": False})
                if vote == -1:
                    like_dislike_ids[0].write({"dislike": True, "like": False})
                if vote == 2:
                    like_dislike_ids[0].write({"like": False})
                if vote == -2:
                    like_dislike_ids[0].write({"dislike": False})
            else:
                if vote == 1:
                    like_dislike_obj.create(
                        {"customer_id": request.uid, "review_id": review_id, "like": True})
                if vote == -1:
                    like_dislike_obj.create(
                        {"customer_id": request.uid, "review_id": review_id, "dislike": True})
            review_obj = request.env['user.review'].browse(review_id)
            res.append(review_obj.likes)
            res.append(review_obj.dislikes)
        return res

    @http.route(['/shop/product/load/review'], type='json', auth="public", website=True)
    def load_review(self, product_id, offset=0, limit=False, **kwargs):
        product_obj = request.env['product.template']
        return_review_obj = product_obj.fetch_active_review2(
            product_id, int(offset), limit)
        values = {
            'review_ids': return_review_obj,
            'product': request.env['product.template'].browse(product_id)
        }
        return request.env.ref("wk_review.wk_review_template").render(values, engine='ir.qweb')

    @http.route(['/shop/product/load/review/count'], type='json', auth="public", website=True)
    def load_review_count(self, product_id, offset=0, limit=False, **kwargs):
        product_obj = request.env['product.template']
        return_review_obj = product_obj.sudo().fetch_active_review2(
            product_id, int(offset), limit)
        return len(return_review_obj)

    @http.route('/wk_review/user.review/<int:res_id>/avatar/<int:partner_id>', type='http', auth='public')
    def avatar(self, res_id, partner_id):
        res_model = "user.review"
        headers = [[('Content-Type', 'image/png')]]
        # default image is one white pixel
        content = 'R0lGODlhAQABAIABAP///wAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='
        if res_model:
            try:
                if request.env[res_model].browse(res_id).partner_id:
                    status, headers, content = binary_content(
                        model='res.partner', id=partner_id, field='image_medium', default_mimetype='image/png', env=request.env(user=SUPERUSER_ID))
                    if not content:
                        status, headers, content = binary_content(model='user.review', id=request.env[res_model].browse(
                            res_id), field='customer_image', default_mimetype='image/png', env=request.env(user=SUPERUSER_ID))
                    if status == 304:
                        return werkzeug.wrappers.Response(status=304)
            except AccessError:
                pass
        image_base64 = base64.b64decode(content)
        headers.append(('Content-Length', len(image_base64)))
        response = request.make_response(image_base64, headers)
        response.status = str(status)
        return response
