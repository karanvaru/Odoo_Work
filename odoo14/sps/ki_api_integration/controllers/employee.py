from odoo import http, _, fields
from odoo.http import request


class Employeeuserlist(http.Controller):

    @http.route('/web/employee/request/list', type='json', auth="user")
    def Employee_user_list(self, **kw):
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
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if limit <= 1:
                limit = 10
            domain = [('employee_id', '!=', False)]
            Employee_user_id = request.env['res.users'].sudo().search(domain, limit=limit, offset=start)
            Employee_user_id_count = request.env['res.users'].search_count(domain)
            if not Employee_user_id:
                return {
                    'code': 200,
                    'message': 'There is no any Employee User',
                    'data': []
                }
            data = []
            for rec in Employee_user_id:
                vals = {
                    'id': rec.id,
                    'name': rec.name,
                    'partner_parent_id': rec.partner_parent_id.name,
                    'login': rec.login,
                }
                data.append(vals)

        except Exception as e:
            return {
                'code': 1001,
                'message': e,
                'data': []
            }
        return {
            'code': 1000,
            'message': 'EmployeeUser List Found Successfully.',
            'data': data,
            'records': Employee_user_id_count
        }

    @http.route('/web/customer/request/list', type='json', auth="user")
    def Customer_user_list(self, **kw):
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
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if limit <= 1:
                limit = 10
            domain = [('employee_id', '=', False)]
            customer_user_id = request.env['res.users'].sudo().search(domain, limit=limit, offset=start)
            customer_user_id_count = request.env['res.users'].search_count(domain)
            if not customer_user_id:
                return {
                    'code': 200,
                    'message': 'There is no any Customer User',
                    'data': []
                }
            data = []
            for rec in customer_user_id:
                vals = {
                    'id': rec.id,
                    'name': rec.name,
                    'partner_parent_id': rec.partner_parent_id.name,
                    'login': rec.login,
                }
                data.append(vals)

        except Exception as e:
            return {
                'code': 1001,
                'message': e,
                'data': []
            }
        return {
            'code': 1000,
            'message': 'CustomerUser List Found Successfully.',
            'data': data,
            'records': customer_user_id_count
        }
