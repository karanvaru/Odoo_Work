from odoo import http, _, fields
from odoo.http import request


class CategoryList(http.Controller):

    @http.route('/web/category/list', type='json', auth="user")
    def category_list(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        try:
            url_params = request.httprequest.args.to_dict()
            start = int(url_params.get('start', 0))
            end = int(url_params.get('end', 0))
            limit = end + 1 - start
            if limit <= 1:
                limit = 10

            category_list = request.env['helpdesk.ticket.category'].sudo().search([], limit=limit, offset=start)
            category_length = request.env['helpdesk.ticket.category'].search_count([])

            if not category_list:
                return {
                    'code': 100,
                    'message': 'Category Not Found!',
                    'data': []
                }
            data = []
            for rec in category_list:
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
            'message': 'Category Found Successfully!',
            'data': data,
            'records': category_length
        }
