from odoo import http
from odoo.http import request


class BestPlatform(http.Controller):

    @http.route('/platform_category/', auth="public", type="json", methods=['POST'])
    def best_platform_category(self):
        platform_category = http.request.env['product.category'].sudo().search([('show_website', '!=', False)])
        return {
            'message': request.env['ir.ui.view']._render_template("cue_website.template_platform_options", {
                'platform': platform_category
            })
        }

    @http.route('/platform_category_images/', auth="public", type="json", methods=['POST'])
    def best_platform_category_images(self, **kwargs):
        product_category_image = http.request.env['product.category'].sudo().search([('id', '=', kwargs['categ_id'])])
        return {
            'message': request.env['ir.ui.view']._render_template("cue_website.template_platform_category", {
                'categ': product_category_image
            })
        }