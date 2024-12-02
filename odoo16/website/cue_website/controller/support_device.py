from odoo import http
from odoo.http import request


class SupportDevice(http.Controller):

    @http.route('/supportdevices/', auth="public", type="json", methods=['POST'])
    def all_device(self):
        support = http.request.env['product.brand'].sudo().search_read([('show_website', '!=', False)], ['name', 'logo'])
        return support

    @http.route('/categorydevice/', auth="public", type="json", methods=['POST'])
    def all_category(self, is_mobile=False):
        product_category = http.request.env['product.category'].sudo().search([('show_website', '!=', False)])
        product_brand = http.request.env['product.brand'].sudo().search([('show_website', '!=', False)])
        return {
            'message': request.env['ir.ui.view']._render_template("cue_website.template_cue_supported_devices_icon", {
                'product_category': product_category,
                'product_brand': product_brand,
                'is_mobile': is_mobile,
            })
        }

    @http.route('/categorybrands/', auth="public", type="json", methods=['POST'])
    def all_category_brands(self,**kwargs):
        product_category = http.request.env['product.category'].sudo().search_read(
            domain=[('id', '=', kwargs['categ_id'])],
            fields=['brand_ids'],
        )
        return product_category

