from odoo import http
from odoo.http import request


class ResourceBlogPage(http.Controller):

    @http.route('/resources_blog_categories/', auth="public", type="json", methods=['POST'])
    def resource_blog_page(self):
        blog_post_ids = http.request.env['blog.post'].sudo().search([('is_published', '=', True), ('url_name', '!=', 'getting-started')])
#         blog_id = blog_post_ids.mapped('blog_id')
        blog_id = blog_post_ids
        print ("blog_id -----",blog_id)
        return {
            'message': request.env['ir.ui.view']._render_template("cue_website.cue_columns", {
                'blog': blog_id
            })
        }

    @http.route('/resources_blog_posts/', auth="public", type="json", methods=['POST'])
    def blog_detail(self,**kwargs):
        id = kwargs['blog_id']
        blog_detail_id = http.request.env['blog.post'].sudo().search([('blog_id.id', '=', id)])
        dct = {}
        for rec in blog_detail_id:
            if rec.blog_id not in dct:
                dct[rec.blog_id] = []
            dct[rec.blog_id].append(rec)
        return {
            'message': request.env['ir.ui.view']._render_template("cue_website.cue_columns_detail", {
                'blog_detail': dct
            })
        }


