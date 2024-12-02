from odoo import http, _, fields
from odoo.http import request


# from odoo.tools import float_repr, html2plaintext

class UserDetails(http.Controller):

    @http.route('/web/user/details', type='json', auth="user")
    def user_details(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        u_user = request.env['res.users'].browse(uid)
        try:
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            res = request.env['res.users'].sudo().search([('id', '=', u_user.id)])
            data = []
            val = {
                'name': res.name,
                'first_name': res.employee_id.firstname,
                'last_name': res.employee_id.lastname,
                'gender': res.employee_id.gender,
                'date_of_birth': res.employee_id.birthday,
                'image_url': base_url + '/web/image/hr.employee/%s/image_1920' % res.employee_id.id,
                'email': res.employee_id.work_email,
                'contact': res.employee_id.work_phone,
                'location': res.employee_id.work_location,

            }
            data.append(val)

        except Exception as e:
            return {
                'code': 100,
                'message': e,
                'data': []
            }
        return {
            'code': 1000,
            'message': 'User Found Successfully!',
            'data': data
        }
