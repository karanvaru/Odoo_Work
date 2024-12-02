from odoo import http, _, fields
from odoo.http import request


class UserPasswordSet(http.Controller):

    # Ticket Create
    @http.route('/web/password/create', type='json', auth="public")
    def user_password_create(self, **kw):
        try:
            login = int(kw.get('login', False))
            if not login:
                return {
                    'code': 1001,
                    'message': 'No any User !!',
                    'data': []
                }
            password = kw.get('password', False)
            if not password:
                return {
                    'code': 1001,
                    'message': 'Please enter Password !!',
                    'data': []
                }
            otp_number = int((kw.get('otp_number', False)))
            res = request.env['res.users'].sudo().search(['&', ('login', '=', login), ('otp_number', '=', otp_number)])
            if not res:
                return {
                    'code': 1001,
                    'message': '!!!Please Give correct OTP!!!',
                    'data': []
                }
            print('company_idddddd', res.company_id)
            res.sudo().otp_validate = True
            data = []
            val = {
                'validation': res.otp_validate
            }
            data.append(val)

            lines = [(0, 0, {
                'user_id': res.id,
                'user_login': login,
                'new_passwd': password
            })]
            wizard_id = request.env['change.password.wizard'].sudo().create({'user_ids': lines})
            wizard_id.change_password_button()
            res.sudo().otp_number = False
            if res.employee_id:
                pass
            else:
                res.sudo().action_create_employee()
                res.employee_id.work_phone = login

        except Exception as e:
            return {
                'code': 1001,
                'message': e,
                'data': []
            }
        return {
            'code': 1000,
            'message': '!! Password Created !!',
            'data': data
        }
