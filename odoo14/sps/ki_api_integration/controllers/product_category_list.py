from odoo import http, _, fields
from odoo.http import request
from odoo.tools import float_repr, html2plaintext


class StageList(http.Controller):

    @http.route('/web/product/category/list', type='json', auth="user")
    def product_category_list(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        res = request.env['res.users'].browse(uid)
        try:
            url_params = request.httprequest.args.to_dict()
            # start = int(url_params.get('start', 0))
            # end = int(url_params.get('end', 0))
            # limit = end + 1 - start
            # if limit < 1:
            #     limit = 10

            category_ls = request.env['product.category'].sudo().search([])
            category_length = request.env['product.category'].search_count([])

            if not category_ls:
                return {
                    'code': 100,
                    'message': 'Product Category Not Found!',
                    'data': []
                }
            data = []
            for rec in category_ls:
                vals = {
                    'id': rec.id,
                    'name': rec.name,
                    'type': rec.type,
                }
                data.append(vals)
        except Exception as e:
            return {
                'code': 100,
                'message': e,
                'data': []
            }

        return {
            'code': 1000,
            'message': 'Product Found Successfully!',
            'data': data,
            'records': category_length
        }
