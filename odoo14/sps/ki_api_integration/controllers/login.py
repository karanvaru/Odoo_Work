from odoo import http, _, fields
from odoo.addons.web.controllers.main import Session
from odoo.http import request


class WEB_LOGIN(Session):

    # Login
    @http.route('/web/session/authenticate', type='json', auth="none")
    def authenticate(self, login, password, db=None, base_location=None):
        if not db:
            db = request.session.db
        login_success = False
        try:
            login_success = request.session.authenticate(db, login, password)
        except:
            pass
        if not login_success:
            return {
                'code': 1001,
                'message': 'Username or password is incorrect!',
                'data': {}
            }
        result = request.env['ir.http'].session_info()
        user = request.env.user
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        user_role = False
        if user.has_group('ki_contract_menu.group_smart_printer_admin'):
            user_role = 'it_admin'
        elif user.has_group('ki_contract_menu.group_smart_printer_administrator'):
            user_role = 'sps_office_administrator'
        elif user.has_group('ki_contract_menu.group_smart_printer_back_office'):
            user_role = 'back_office'
        elif user.has_group('ki_contract_menu.group_smart_printer_service_engineer'):
            user_role = 'service_engineer'
        elif user.has_group('ki_contract_menu.group_smart_printer_customer_user'):
            user_role = 'register_user'
        elif user.has_group('ki_contract_menu.group_smart_printer_guest_user'):
            user_role = 'guest_user'
        elif user.has_group('ki_contract_menu.group_smart_printer_owner'):
            user_role = 'owner'

        result.update({
            "image_url": base_url + '/web/image/res.users/%s/image_128' % user.id,
            'company_name': user.company_id.name,
            'user_id': {
                'user_id': user.id,
                'user_role': user_role
            }
        })
        return {
            'code': 1000,
            'message': 'You are successfully logged in!',
            'data': result
        }

    @http.route('/web/user/info', type='json', auth="user")
    def user_info(self):
        uid = request.session.uid

        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }

        result = request.env['ir.http'].session_info()
        user = request.env.user
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        user_role = False
        if user.has_group('ki_contract_menu.group_smart_printer_admin'):
            user_role = 'it_admin'
        elif user.has_group('ki_contract_menu.group_smart_printer_administrator'):
            user_role = 'sps_office_administrator'
        elif user.has_group('ki_contract_menu.group_smart_printer_back_office'):
            user_role = 'back_office'
        elif user.has_group('ki_contract_menu.group_smart_printer_service_engineer'):
            user_role = 'service_engineer'
        elif user.has_group('ki_contract_menu.group_smart_printer_customer_user'):
            user_role = 'register_user'
        elif user.has_group('ki_contract_menu.group_smart_printer_guest_user'):
            user_role = 'guest_user'
        elif user.has_group('ki_contract_menu.group_smart_printer_owner'):
            user_role = 'owner'

        result.update({
            "image_url": base_url + '/web/image/res.users/%s/image_128' % user.id,
            'company_name': user.company_id.name,
            'user_id': {
                'user_id': user.id,
                'user_role': user_role
            }
        })

        device_id = request.httprequest.headers.get("Device-Id")
        device_type = request.httprequest.headers.get("Device-Type")
        try:
            #           user_id = request.env['res.users'].browse(uid)
            res = request.env['res.mobile.user'].sudo().search([('device_id', '=', device_id)])
            if res:
                res.unlink()
            sessin_id = user.mobi_device_ids.filtered(lambda l: l.session_id == request.session.sid)
            if not sessin_id:
                user.mobi_device_ids = [(0, 0, {
                    'device_id': device_id,
                    'device_type': device_type,
                    'session_id': request.session.sid
                })]
        except:
            pass
        cookies = request.httprequest.cookies

        return {
            'code': 1000,
            'message': 'User information',
            'data': result
        }

    # LOGOUT
    @http.route('/web/session/user/logout', type='json', auth="none")
    def session_logout(self):
        uid = request.session.uid

        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }

        user = request.env['res.users'].sudo().browse(uid)
        user.mobi_device_ids.filtered(lambda l: l.session_id == request.session.sid).unlink()

        request.session.logout()
        return {
            'code': 1000,
            'message': 'You are successfully logged out!',
            'data': []
        }
