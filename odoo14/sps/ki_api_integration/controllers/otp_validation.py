from odoo import http, _, fields
from odoo.addons.web.controllers.main import Session
from odoo.http import request


class OtpConfirm(http.Controller):
    @http.route('/web/otp/validation', type='json', auth="public")
    def otp_validation_user(self, **kw):
        try:
            login = kw.get('login', False)
            otp_number = int((kw.get('otp_number', False)))
            res = request.env['res.users'].sudo().search([('login', '=', login)])
            if res.otp_number != otp_number:
                return {
                    'code': 101,
                    'message': '!! OTP is not Valid !!',
                    'data': []
                }
        except Exception as e:
            return {
                'code': 1001,
                'message': e,
                'data': []
            }
        return {
            'code': 1000,
            'message': 'OTP Confirm !!',
            'data': []
        }
