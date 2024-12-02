from odoo import http, _, fields
from odoo.http import request
from odoo import SUPERUSER_ID
import random
import math


class UserCreate(http.Controller):

    # USer Create
    @http.route('/web/user/create', type='json', auth="none")
    def create_user(self, **kw):

        user_cre = request.env['res.users'].sudo()
        try:
            is_forgot_password = kw.get('is_forgot_password', False)
            number = int(kw.get('number', False))
            if not number:
                return {
                    'code': 1001,
                    'message': 'Please Enter Your Phone Number!',
                    'data': []
                }
            name = kw.get('name', False)
            if not name and is_forgot_password == False:
                return {
                    'code': 1001,
                    'message': 'Please Enter Name!',
                    'data': []
                }
            res = request.env['res.users'].sudo().search([('login', '=', number)])
            if not res:
                if is_forgot_password:
                    return {
                        'code': 1001,
                        'message': 'User Not Found !!',
                        'data': []
                    }
                else:
                    company_uid = request.env['res.users'].sudo().browse(SUPERUSER_ID).company_id
                    company_uids = request.env['res.users'].sudo().browse(SUPERUSER_ID).company_ids
                    for r in company_uids:
                        r_id = r.id
                    group_id = request.env.ref('ki_contract_menu.group_smart_printer_guest_user').id
                    id = request.env.ref('base.group_user').id
                    user_vals = user_cre.default_get(user_cre._fields)
                    if kw.get('id'):
                        del kw['id']
                    columns = list(kw.keys())
                    new_column = []
                    for colum in columns:
                        if colum in user_cre._fields:
                            new_column.append(colum)
                    for colum in new_column:
                        user_vals[colum] = kw.get(colum)
                    user_vals.update({
                        'name': name,
                        'login': number,
                        'company_id': company_uid.id,
                        'company_ids': [(6, 0, [r_id])],
                        'groups_id': [(6, 0, [id, group_id])]
                    })

                    usr_id = user_cre.create(user_vals)
                    digits = [i for i in range(0, 10)]
                    random_str = ""
                    for i in range(6):
                        index = math.floor(random.random() * 10)
                        random_str += str(digits[index])
                    usr_id.otp_number = random_str
            else:
                if is_forgot_password:
                    digits = [i for i in range(0, 10)]
                    random_str = ""
                    for i in range(6):
                        index = math.floor(random.random() * 10)
                        random_str += str(digits[index])
                    res.otp_number = random_str
                    res.otp_validate = False
                else:
                    if res.otp_validate != True:

                        res.update({
                            'name': name,
                        })
                        digits = [i for i in range(0, 10)]
                        random_str = ""
                        for i in range(6):
                            index = math.floor(random.random() * 10)
                            random_str += str(digits[index])
                        res.otp_number = random_str
                    else:
                        return {
                            'code': 1000,
                            'message': '!! User Already Created !!',
                            'data': [{
                                    'user_created': True
                            }]
                        }

        except Exception as e:
            return {
                'code': 1001,
                'message': e,
                'data': []
            }
        return {
            'code': 1000,
            'message': 'User Created Successfully!',
        }
