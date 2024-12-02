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

import odoo
from odoo import tools, api
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging, base64
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def _set_avg_rating(self):
        """ """
        add = 0.0
        avg = 0.0
        for obj in self:
            if obj.user_review:
                for reviews_obj in obj.user_review:
                    add += reviews_obj.rating
                avg = add / len(obj.user_review)
            obj.average_rating = avg

    user_review = fields.One2many(
        'user.review', 'template_id', string='Review')
    average_rating = fields.Float(
        compute='_set_avg_rating', string="Average Rating")

    def fetch_active_review(self, product_id):
        if product_id:
            review_ids = self.env["user.review"].search(
                [('template_id', '=', product_id), ('website_published', '=', True)])
            return review_ids
        else:
            return []

    def fetch_active_review2(self, product_id, offset=0, limit=False):
        review_ids = self.env["user.review"].search(
            [('template_id', '=', product_id), ('website_published', '=', True)])
        return_obj = []
        if review_ids and offset < len(review_ids):
            while offset < len(review_ids) and limit != 0:
                return_obj.append(review_ids[offset])
                offset += 1
                limit -= 1
            return return_obj
        else:
            return []

    def avg_review(self):
        val = 0.0
        length = 0.0
        if self._ids:
            reviews_obj = self.fetch_active_review(self._ids[0])
            if reviews_obj:
                for obj in reviews_obj:
                    val += float(obj.rating)
                    length = float(len(reviews_obj))
                return round((val / length), 1)
        return 0

    @api.one
    def temp_review(self):
        value = self.avg_review()
        if value:
            dec = int(value)
            frac = int((value - dec) / .1)
            if frac in [1, 2]:
                frac = 2
            elif frac in [3, 4]:
                frac = 4
            elif frac in [5, 6]:
                frac = 6
            elif frac in [7, 8, 9]:
                frac = 8
            return [dec, frac]
        return [0, 0]

    @api.multi
    def fetch_user_vote(self, review_id):
        like_dislike = self.env["review.like.dislike"]
        like_dislike_id = like_dislike.search(
            [('customer_id', '=', self._uid), ('review_id', '=', review_id)])
        if like_dislike_id:
            result = [like_dislike_id[0].like, like_dislike_id[0].dislike]
            return result
        return [False, False]

    @api.model
    def get_review_current_time(self, review_id):
        review_pool = self.env["user.review"]
        if review_id:
            review_obj = review_pool.browse(review_id)
            iso_format = review_obj.create_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            return iso_format

    @api.multi
    def action_avg_review_fun(self):
        self.ensure_one()
        action = self.env.ref('wk_review.action_user_review')
        list_view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'wk_review.product_user_review_tree_view_webkul')
        form_view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'wk_review.product_user_review_form_view_webkul')
        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'res_model': action.res_model,
            'domain': "[('template_id','=',%s)]" % self._ids[0],
        }

    @api.model
    def get_limit(self):
        config_setting_obj = self.env[
            'website.review.config'].sudo().get_values()
        if config_setting_obj.get('review_no'):
            return config_setting_obj['review_no']
        else:
            return 0


class UserReview(models.Model):
    _name = "user.review"
    _rec_name = 'customer'
    _description = "Review"
    # _inherit = ['ir.needaction_mixin', 'website.published.mixin']
    _inherit = ['website.published.mixin']

    _order = "website_published desc, create_date desc"

    @api.model
    def create(self, vals):
        if vals.get('rating'):
            if vals['rating'] <= 0:
                raise UserError('Warning Rating must be more than zero')
            if vals['rating'] > 5:
                raise UserError('Warning Rating can not be more than 5')
        return super(UserReview, self).create(vals)

    @api.one
    def write(self, vals):
        if vals.get('rating'):
            if vals['rating'] <= 0:
                raise UserError('Warning Rating must be more than zero')
            if vals['rating'] > 5:
                raise UserError('Warning Rating can not be more than 5')
        return super(UserReview, self).write(vals)

    @api.model
    def _get_name(self):
        res_obj = self.env['res.users'].browse(self._uid)
        name = res_obj.name
        return name

    @api.model
    def _get_partner(self):
        return self.env['res.partner'].browse(self.env['res.users'].browse(self._uid).partner_id).id

    @api.model
    def _get_mail(self):
        res_obj = self.env['res.users'].browse(self._uid)
        email = res_obj.email
        return email

    @api.model
    def _get_image(self):
        res_obj = self.env['res.users'].browse(self._uid)
        image = res_obj.image
        return image

    @api.model
    def _get_auto_website_published(self):
        config_setting_obj = self.env[
            'website.review.config'].sudo().get_values()
        if config_setting_obj.get('auto_publish'):
            return config_setting_obj['auto_publish']
        else:
            return False

    @api.multi
    def _set_total_likes(self):
        """ """
        for obj in self:
            like_dislike_ids = obj.env["review.like.dislike"].search(
                [('like', '=', True), ('review_id', '=', obj.id)])
            obj.likes = len(like_dislike_ids)

    @api.multi
    def _get_rating(self):
        """ """
        for obj in self:
            obj.rating2 = obj.rating

    @api.multi
    def _set_total_dislikes(self):
        """ """
        for obj in self:
            like_dislike_ids = obj.env["review.like.dislike"].search(
                [('dislike', '=', True), ('review_id', '=', obj.id)])
            obj.dislikes = len(like_dislike_ids)

    @api.multi
    def _set_total_votes(self):
        """ """
        for obj in self:
            like_dislike_ids = obj.env["review.like.dislike"].search(
                [('review_id', '=', obj.id)])
            obj.total_votes = len(like_dislike_ids)

    @api.depends('website_published')
    def _get_value_website_published(self):
        for record in self:
            if record.website_published:
                record.state = 'pub'
            else:
                record.state = 'unpub'

    @api.model
    def _get_default_image(self, is_company, colorize=False):
        img_path = odoo.modules.get_module_resource(
            'base', 'static/img', 'company_image.png' if is_company else 'avatar.png')
        with open(img_path, 'rb') as f:
            image = f.read()
        # colorize user avatars
        if not is_company and colorize:
            image = tools.image_colorize(image)
        _logger.info("================%r",tools.image_resize_image_big(base64.encodestring(image)))
        return tools.image_resize_image_big(base64.encodestring(image))
        # return tools.image_resize_image_big(image.encode('base64'))

    title = fields.Char(string='Title', required=True)
    active = fields.Boolean(string="Active", default=True)
    msg = fields.Text(string='Message', required=True)
    rating = fields.Integer(string='Rating')
    rating2 = fields.Integer(compute="_get_rating", string="Rating")
    customer = fields.Char(string='Customer', default=_get_name)
    customer_image = fields.Binary(string='Customer Image', widget="image",
                                   default=lambda self: self._get_default_image(False, False))
    email = fields.Char(string='Email', default=_get_mail)
    website_published = fields.Boolean(
        'Available on the website', copy=False, default=_get_auto_website_published)
    template_id = fields.Many2one('product.template', string='Product')
    create_date = fields.Datetime(string='Created Date')
    likes = fields.Integer(compute='_set_total_likes', string='Likes')
    dislikes = fields.Integer(compute='_set_total_dislikes', string='Dislikes')
    total_votes = fields.Integer(
        compute='_set_total_votes', string='Lotal Votes')
    like_dislike_ids = fields.One2many(
        'review.like.dislike', 'review_id', string="Like/Dislike")
    state = fields.Selection([('pub', 'Published'), ('unpub', 'Unpublished')],
                             compute='_get_value_website_published', store=True)
    partner_id = fields.Many2one("res.partner", string="Customer", default=_get_partner)

    @api.multi
    def action_review_likes_fun(self):
        self.ensure_one()
        action = self.env.ref('wk_review.action_reviews_likes_list')
        list_view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'wk_review.wk_review_likes_tree_view')
        form_view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'wk_review.wk_review_like_dislike_Form_view')
        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'res_model': action.res_model,
            'domain': "[('like','=',True),('review_id','=',%s)]" % self._ids[0],
        }

    @api.multi
    def action_review_dislikes_fun(self):
        self.ensure_one()
        action = self.env.ref('wk_review.action_reviews_dislikes_list')
        list_view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'wk_review.wk_review_dislikes_tree_view')
        form_view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'wk_review.wk_review_like_dislike_Form_view')
        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': "{'default_review_id': " + str(self._ids[0]) + "}",
            'res_model': action.res_model,
            'domain': "[('dislike','=',True),('review_id','=',%s)]" % self._ids[0],
        }

    @api.one
    def website_publish_button(self):
        self.website_published = True

    @api.one
    def website_unpublish_button(self):
        self.website_published = False


class ReviewLikeDislike(models.Model):
    _name = "review.like.dislike"
    _order = "create_date DESC"

    customer_id = fields.Many2one('res.users', string='User')
    name = fields.Char(related='customer_id.name', string="Customer")
    like = fields.Boolean(string='Like', default=False)
    dislike = fields.Boolean(string='Dislike', default=False)
    review_id = fields.Many2one("user.review")

    @api.multi
    def _single_user_per_product(self):
        x = self.search([('customer_id', '=', self.customer_id.id),
                         ('review_id', '=', self.review_id.id)])
        if len(x) > 1:
            return False
        else:
            return True

    _constraints = [
        (_single_user_per_product, 'Error ! You have already like or dislike this review.', [
         'customer_id', 'review_id'])
    ]

    @api.onchange('like')
    def on_change_like(self):
        if self.like:
            self.dislike = False

    @api.onchange('dislike')
    def on_change_dislike(self):
        if self.dislike:
            self.like = False
