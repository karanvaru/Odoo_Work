from odoo import http
from odoo.http import request


class OutOfBpx(http.Controller):

    @http.route('/prepare_out_of_box_list/', auth="public", type="json", methods=['POST'])
    def prepare_out_of_box_list(self, **kwargs):
        result = http.request.env['product.brand'].sudo().prepare_out_of_box_list()
        return result

    @http.route('/web/brand/<int:brand_id>', type='http', auth="public", website=True, sitemap=True)
    def redirect_brand_url(self, brand_id, **kwargs):
        url = '/'
        brand = http.request.env['product.brand'].sudo().browse(brand_id)
        if brand.redirect_url:
            url = brand.redirect_url
        return url
