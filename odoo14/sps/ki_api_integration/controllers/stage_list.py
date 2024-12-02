from odoo import http, _, fields
from odoo.http import request
from odoo.tools import float_repr, html2plaintext


class StageList(http.Controller):

    @http.route('/web/stage/list', type='json', auth="user")
    def stage_list(self, **kw):
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
            start = int(url_params.get('start', 0))
            end = int(url_params.get('end', 0))
            limit = end + 1 - start
            if limit <= 1:
                limit = 10

            stage_ls = request.env['helpdesk.ticket.stage'].sudo().search([], limit=limit, offset=start)
            stage_length = request.env['helpdesk.ticket.stage'].search_count([])

            if not stage_ls:
                return {
                    'code': 100,
                    'message': 'Stage Not Found!',
                    'data': []
                }
            data = []
            for rec in stage_ls:
                vals = {
                    'id': rec.id,
                    'name': rec.name,
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
            'message': 'Stage Found Successfully!',
            'data': data,
            'records': stage_length
        }
