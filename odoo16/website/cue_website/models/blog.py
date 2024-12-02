# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
import random

from odoo import api, models, fields, _


class BlogPost(models.Model):
    _inherit = "blog.post"

    url_name = fields.Char(
        'Blog Name'
    )
    custom_website_url = fields.Char(
        'Custom Website',
        compute='_compute_custom_website_url',
        copy=False
    )
    blog_img = fields.Binary(
        string="Image",
    )
    

    @api.depends('blog_id')
    def _compute_custom_website_url(self):
        for rec in self:
            if rec.blog_id and rec.blog_id.url_category and rec.url_name:
                rec.custom_website_url = 'blog/{}/{}'.format(rec.blog_id.url_category, rec.url_name)
            else:
                rec.custom_website_url = ''


    def _compute_website_url(self):
        super(BlogPost, self)._compute_website_url()
        for blog_post in self:
            blog_post.website_url = "/blog/%s/%s" % (blog_post.blog_id.url_category, blog_post.url_name)


class BlogBlog(models.Model):
    _inherit = "blog.blog"

    url_category = fields.Char('Blog Category')
