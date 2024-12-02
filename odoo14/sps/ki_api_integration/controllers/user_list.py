from odoo import http, _, fields
from odoo.http import request
from odoo.tools import float_repr, html2plaintext


class UserList(http.Controller):

    @http.route('/web/user/list', type='json', auth="user")
    def user_list(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        res = request.env['res.users'].sudo().search([])
        try:
            name = kw.get('name', False)
            url_params = request.httprequest.args.to_dict()
            start = int(url_params.get('start', 0))
            end = int(url_params.get('end', 0))
            limit = end + 1 - start
            if limit <= 1:
                limit = 10
            line = res.filtered(lambda i: i.has_group('ki_contract_menu.group_smart_printer_service_engineer'))
            domain = []
            if name and name != '':
                domain = [('name', '=', name)]
            if line:
                group_id = request.env.ref('ki_contract_menu.group_smart_printer_service_engineer')
                user_ls_id = group_id.users
                user_ls = request.env['res.users'].sudo().search([('id', 'in', user_ls_id.ids)] + domain, limit=limit,
                                                                 offset=start)
                user_length = request.env['res.users'].search_count([('id', 'in', user_ls_id.ids)] + domain)
            else:
                user_ls = request.env['res.users'].sudo().search([] + domain, limit=limit, offset=start)
                user_length = request.env['res.users'].search_count([] + domain)
            if not user_ls:
                return {
                    'code': 100,
                    'message': 'User Not Found!',
                    'data': []
                }
            data = []
            for rec in user_ls:
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
            'message': 'User Found Successfully!',
            'data': data,
            'records': user_length
        }

    # @http.route('/web/user/search', type='json', auth="user")
    # def user_search(self, **kw):
    #     uid = request.session.uid
    #     if not uid:
    #         return {
    #             'code': 100,
    #             'message': 'Session Expired!',
    #             'data': []
    #         }
    #     try:
    #         name = kw.get('name', False)
    #         url_params = request.httprequest.args.to_dict()
    #         start = int(url_params.get('start', 0))
    #         end = int(url_params.get('end', 0))
    #         limit = end + 1 - start
    #         if limit <= 1:
    #             limit = 10
    #         domain = [('name', '=', name)]
    #         user_id_length = request.env['res.users'].sudo().search_count(domain)
    #         user = request.env['res.users'].sudo().search(domain, limit=limit, offset=start, order='name')
    #         data = []
    #         base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #         for rec in user:
    #             data.append(
    #                 {
    #                     'id': rec.id,
    #                     'name': rec.name,
    #                     'first_name': rec.employee_id.firstname,
    #                     'last_name': rec.employee_id.lastname,
    #                     'gender': rec.employee_id.gender,
    #                     'date_of_birth': rec.employee_id.birthday,
    #                     'image_url': base_url + '/web/image/hr.employee/%s/image_1920' % rec.employee_id.id,
    #                     'email': rec.employee_id.work_email,
    #                     'contact': rec.employee_id.work_phone,
    #                     'location': rec.employee_id.work_location,
    #                 }
    #             )
    #     except Exception as e:
    #         return {
    #             'code': 100,
    #             'message': e,
    #             'data': []
    #         }
    #
    #     return {
    #         'code': 1000,
    #         'message': 'User Found Successfully!',
    #         'data': data,
    #         'records': user_id_length
    #     }
