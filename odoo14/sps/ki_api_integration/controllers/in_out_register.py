import dateutil.utils
from odoo import http, _, fields
from odoo.http import request


class InOutRegister(http.Controller):

    # Register Create
    @http.route('/web/in/out/register/create', type='json', auth="user")
    def in_out_product_register(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        product_register_id = request.env['product.in.out.register'].sudo().search([])
        try:
            # product_id = int(kw.get('product_id', False))
            operation_type = kw.get('operation_type', False)
            if not operation_type:
                return {
                    'code': 200,
                    'message': 'Please add Operation',
                    'data': []
                }
            assign_user_id = int(kw.get('assign_user', False))
            partner_id = int(kw.get('partner_id', False))
            domain = [('date', '=', dateutil.utils.today()), ('assign_user', '=', assign_user_id)]
            register_id = request.env['product.in.out.register'].sudo().search(domain, limit=1)
            # product_register_val = product_register_id.default_get(product_register_id._fields)
            # product_new_id = request.env['product.product'].browse(product_id)
            product_register = []
            data = []
            if operation_type == 'out':
                if register_id:
                    for rec in kw.get('product_ids', []):
                        product_new_id = request.env['product.product'].browse(int(rec['product_id']))
                        new_line = request.env['product.in.out.register.lines'].sudo().search(
                            [('product_id', '=', product_new_id.id), ('operation_type', '=', operation_type),
                             ('register_id', '=', register_id.id)])
                        if new_line:
                            return {
                                'code': 101,
                                'message': 'Product(%s) Already Register' % (new_line.product_id.display_name),

                            }
                        else:
                            res_line = request.env['product.in.out.register.lines'].create({
                                'register_id': register_id.id,
                                'product_id': product_new_id.id,
                                'name': product_new_id.name,
                                'uom_id': product_new_id.uom_id.id,
                                'operation_type': operation_type,
                                'partner_id': partner_id,
                                'state': 'with_user'
                            })
                            data.append(res_line)
                else:
                    for rec in kw.get('product_ids', []):
                        product_new_id = request.env['product.product'].browse(int(rec['product_id']))
                        vals = {
                            'product_id': product_new_id.id,
                            'name': product_new_id.name,
                            'uom_id': product_new_id.uom_id.id,
                            'operation_type': operation_type,
                            'partner_id': partner_id,
                            'state':'with_user'
                        }
                        product_register.append((0, 0, vals))
                    res = product_register_id.sudo().create({
                        'assign_user': assign_user_id,
                        'line_ids': product_register
                    })
            elif operation_type == 'in':
                if register_id:
                    for rec in kw.get('product_ids', []):
                        product_new_id = request.env['product.product'].browse(int(rec['product_id']))
                        new_line = request.env['product.in.out.register.lines'].sudo().search(
                            [('product_id', '=', product_new_id.id), ('operation_type', '=', operation_type),
                             ('register_id', '=', register_id.id)])
                        if new_line:
                            new_line.update({
                                'state': 'with_office'
                            })
                            # return {
                            #     'code': 101,
                            #     'message': 'Product(%s) Already Register' % (new_line.product_id.display_name),
                            #
                            # }
                        else:
                            return {
                                'code': 101,
                                'message': 'Product(%s) not Found in  Register' % (new_line.product_id.display_name),

                            }
                            # res_line = request.env['product.in.out.register.lines'].create({
                            #     'register_id': register_id.id,
                            #     'product_id': product_new_id.id,
                            #     'name': product_new_id.name,
                            #     'uom_id': product_new_id.uom_id.id,
                            #     'operation_type': operation_type,
                            #     'partner_id': partner_id,
                            #     'state': 'with_office'
                            # })
                            # data.append(res_line)
                else:
                    for rec in kw.get('product_ids', []):
                        product_new_id = request.env['product.product'].browse(int(rec['product_id']))
                        vals = {
                            'product_id': product_new_id.id,
                            'name': product_new_id.name,
                            'uom_id': product_new_id.uom_id.id,
                            'operation_type': operation_type,
                            'partner_id': partner_id,
                            'state': 'with_office'
                        }
                        product_register.append((0, 0, vals))
                    res = product_register_id.sudo().create({
                        'assign_user': assign_user_id,
                        'line_ids': product_register
                    })
        except Exception as e:
            return {
                'code': 1001,
                'message': e,
                'data': []
            }
        return {
            'code': 1000,
            'message': 'Registration Completed Successfully!',
        }

    # @http.route('/web/in/out/register/edit', type='json', auth="user")
    # def in_out_product_register_edit(self, **kw):
    #     uid = request.session.uid
    #     if not uid:
    #         return {
    #             'code': 100,
    #             'message': 'Session Expired!',
    #             'data': []
    #         }
    #     try:
    #         id = int(kw.get('id', False))
    #         new_id = 0
    #         for rec in kw.get('lines', []):
    #             new_id = request.env['product.in.out.register'].browse(id)
    #             new_line_id = request.env['product.in.out.register.lines'].browse(rec['line_id'])
    #             res = new_line_id.update({
    #                 'partner_id': rec['partner_id']
    #             })
    #         line_lis = []
    #         vals = {
    #             'id': new_id.id,
    #             'name': new_id.name,
    #             'date': new_id.date,
    #             'user_id': {
    #                 'id': new_id.user_id.id,
    #                 'name': new_id.user_id.name,
    #             },
    #             'company_id': {
    #                 'id': new_id.company_id.id,
    #                 'name': new_id.company_id.name,
    #             },
    #             'line_ids': line_lis
    #         }
    #         for line in new_id.line_ids:
    #             val = {
    #                 'id': line.id,
    #                 'name': line.name,
    #                 'uom_id': {
    #                     'id': line.uom_id.id,
    #                     'name': line.uom_id.name,
    #                 },
    #                 'quantity': line.quantity,
    #                 'comment': line.comment,
    #                 'operation_type': line.operation_type,
    #                 'partner_id': {
    #                     'id': line.partner_id.id,
    #                     'name': line.partner_id.name,
    #                 },
    #             }
    #             line_lis.append(val)
    #     except Exception as e:
    #         return {
    #             'code': 1001,
    #             'message': e,
    #             'data': []
    #         }
    #     return {
    #         'code': 1000,
    #         'message': 'Registration Edited Successfully!',
    #         'data': vals,
    #
    #     }

    @http.route('/web/in/out/register/edit', type='json', auth="user")
    def in_out_product_register_edit(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        try:
            # register_id = int(kw.get('register_id', False))
            # operation_type = kw.get('operation_type', False)
            # new_id = 0
            for rec in kw.get('remove_product_ids', []):
                # new_id = request.env['product.in.out.register'].browse(register_id)
                # product_new_id = request.env['product.product'].browse(int(rec['product_id']))
                new_line_id = request.env['product.in.out.register.lines'].browse(int(rec['line_id']))
                re = new_line_id.unlink()
                # new_line_id = request.env['product.in.out.register.lines'].search(
                #     [('product_id', '=', product_new_id.id), ('register_id', '=', new_id.id)])
                # if not new_line_id:
                #     return {
                #         'code': 1001,
                #         'message': 'Product Not Found!',
                #     }
            # line_lis = []
            # vals = {
            #     'id': new_id.id,
            #     'name': new_id.name,
            #     'date': new_id.date,
            #     'user_id': {
            #         'id': new_id.user_id.id,
            #         'name': new_id.user_id.name,
            #     },
            #     'company_id': {
            #         'id': new_id.company_id.id,
            #         'name': new_id.company_id.name,
            #     },
            #     'line_ids': line_lis
            # }
            # for line in new_id.line_ids:
            #     val = {
            #         'id': line.id,
            #         'name': line.name,
            #         'uom_id': {
            #             'id': line.uom_id.id,
            #             'name': line.uom_id.name,
            #         },
            #         'quantity': line.quantity,
            #         'comment': line.comment,
            #         'operation_type': line.operation_type,
            #         'partner_id': {
            #             'id': line.partner_id.id,
            #             'name': line.partner_id.name,
            #         },
            #     }
            #     line_lis.append(val)
        except Exception as e:
            return {
                'code': 1001,
                'message': e,
                'data': []
            }
        return {
            'code': 1000,
            'message': 'Product Remove Successfully!',
            # 'data': vals,
        }

    @http.route('/web/in/out/register/ticket/delete', type='json', auth="user")
    def in_out_product_register_delete(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        try:
            for rec in kw.get('remove_ticket_line_ids', []):
                new_line_id = request.env['product.in.out.register.lines'].browse(int(rec['line_id']))
                new_line_id.update({
                    'ticket_id': False,
                    'partner_id': False,
                    'state': False
                })
                # new_line_id.ticket_id = False
                # new_line_id.partner_id = False
                # new_line_id.state = False

        except Exception as e:
            return {
                'code': 1001,
                'message': e,
                'data': []
            }
        return {
            'code': 1000,
            'message': 'Ticket Remove Successfully!',
            # 'data': vals,
        }

    @http.route('/web/in/out/register/list', type='json', auth="user")
    def in_out_product_register_list(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        res_user_id = request.env['res.users'].browse(uid)
        try:
            url_params = request.httprequest.args.to_dict()
            start = int(url_params.get('start', 0))
            end = int(url_params.get('end', 0))
            limit = end + 1 - start
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if limit <= 1:
                limit = 10
            pro_register_id = request.env['product.in.out.register'].sudo().search([], limit=limit, offset=start,
                                                                                   order='write_date desc')
            pro_register_length = request.env['product.in.out.register'].search_count([])
            if not pro_register_id:
                return {
                    'code': 100,
                    'message': 'There is no any Product Register',
                    'data': [],
                    'line_lis': []
                }
            if request.env.user.has_group('ki_contract_menu.group_smart_printer_service_engineer'):
                domain = [('assign_user', '=', res_user_id.id)]
                pro_register_id = request.env['product.in.out.register'].sudo().search(domain, limit=limit,
                                                                                       offset=start,
                                                                                       order='write_date desc')
                pro_register_length = request.env['product.in.out.register'].search_count(domain)
            data = []
            for rec in pro_register_id:
                line_lis = []
                vals = {
                    'id': rec.id,
                    'name': rec.name,
                    'date': rec.date,
                    'quantity_income': rec.quantity_income,
                    'quantity_outcome': rec.quantity_outcome,
                    'assign_user': {
                        'id': rec.assign_user.id,
                        'name': rec.assign_user.name,
                    },
                    'user_id': {
                        'id': rec.user_id.id,
                        'name': rec.user_id.name,
                    },
                    'company_id': {
                        'id': rec.company_id.id,
                        'name': rec.company_id.name,
                    },
                    'line_ids': line_lis
                }
                data.append(vals)
                for line in rec.line_ids:
                    val = {
                        'id': line.id,
                        'name': line.name,
                        'uom_id': {
                            'id': line.uom_id.id,
                            'name': line.uom_id.name,
                        },
                        'quantity': line.quantity,
                        'comment': line.comment,
                        'operation_type': line.operation_type,
                        'partner_id': {
                            'id': line.partner_id.id,
                            'name': line.partner_id.name,
                        },
                    }
                    line_lis.append(val)

        except Exception as e:
            return {
                'code': 1001,
                'message': e,
                'data': [],
                'line_lis': []
            }

        return {
            'code': 1000,
            'message': 'Record Found Successfully!',
            'data': data,
            'records': pro_register_length

        }

    @http.route('/web/in/out/register/detail', type='json', auth="user")
    def in_out_product_register_details(self, **kw):
        state_label ={}
        state_2 = request.env['product.in.out.register.lines'].fields_get(allfields=['state'])['state']['selection']
        for state_name in state_2:
            state_label[state_name[0]] = state_name[1]

        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        try:
            product_register_id = int(kw.get('product_register_id', False))
            domain = [('id', '=', product_register_id)]
            register_id = request.env['product.in.out.register'].sudo().search(domain)
            if not register_id:
                return {
                    'code': 100,
                    'message': 'There is no any Product Register',
                    'data': [],
                    'line_lis': []
                }
            line_lis = []
            vals = {
                'id': register_id.id,
                'name': register_id.name,
                'date': register_id.date,
                'quantity_income': register_id.quantity_income,
                'quantity_outcome': register_id.quantity_outcome,
                'assign_user': {
                    'id': register_id.assign_user.id,
                    'name': register_id.assign_user.name,
                },
                'user_id': {
                    'id': register_id.user_id.id,
                    'name': register_id.user_id.name,
                },
                'company_id': {
                    'id': register_id.company_id.id,
                    'name': register_id.company_id.name,
                },
                'line_ids': line_lis
            }
            for line in register_id.line_ids:
                val = {
                    'id': line.id,
                    'name': line.name,
                    'product_id': {
                        'id': line.product_id.id,
                        'name': line.product_id.display_name
                    },
                    'uom_id': {
                        'id': line.uom_id.id,
                        'name': line.uom_id.name,
                    },
                    'quantity': line.quantity,
                    'comment': line.comment,
                    'operation_type': line.operation_type,
                    'partner_id': {
                        'id': line.partner_id.id,
                        'name': line.partner_id.display_name,
                    },
                    # 'state': line.state,
                    'state':  state_label[line.state],
                }
                line_lis.append(val)

        except Exception as e:
            return {
                'code': 1001,
                'message': e,
                # 'data': [],
                # 'line_lis': []
            }

        return {
            'code': 1000,
            'message': 'Register Found Successfully',
            'data': vals,
            # 'records': register_length
        }

    @http.route('/web/in/out/register/deliver', type='json', auth="user")
    def in_out_product_register_deliver(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        r_user = request.env['res.users'].browse(uid)
        try:
            # product_id = int(kw.get('product_id', False))
            partner_id = int(kw.get('partner_id', False))
            assign_user_id = int(kw.get('assign_user', False))
            ticket_id = int(kw.get('ticket_id', False))
            # product_browse_id = request.env['product.product'].browse(product_id)
            ticket_browse_id = request.env['helpdesk.ticket'].browse(ticket_id)
            domain = [('date', '=', dateutil.utils.today()), ('assign_user', '=', r_user.id)]
            register_id = request.env['product.in.out.register'].search(domain, limit=1)
            product_register = []
            data = []
            if ticket_id:
                if not register_id:
                    for product in kw.get('product_ids', []):
                        product_id = request.env['product.product'].browse(int(product['product_id']))
                        vals = {
                            'product_id': product_id.id,
                            'name': product_id.display_name,
                            'uom_id': product_id.uom_id.id,
                            'operation_type': 'out',
                            'partner_id': ticket_browse_id.partner_id.id,
                            'ticket_id': ticket_id,
                            'state':'with_customer'
                        }
                        product_id.sudo().customer_id = ticket_browse_id.partner_id.id
                        product_id.sudo().partner_shipping_pro_id = ticket_browse_id.partner_id.id
                        product_register.append((0, 0, vals))
                    res = request.env['product.in.out.register'].sudo().create({
                        'line_ids': product_register,
                        'assign_user': r_user.id,
                    })
                    data.append(product_register)
                else:
                    for product in kw.get('product_ids', []):
                        product_id = request.env['product.product'].browse(int(product['product_id']))
                        line = register_id.line_ids.filtered(lambda i: i.product_id == product_id)
                        if line:
                            res_update = line.update({
                                'partner_id': ticket_browse_id.partner_id.id,
                                'ticket_id': ticket_id,
                                'state':'with_customer'
                            })
                            product_id.sudo().customer_id = ticket_browse_id.partner_id.id
                            product_id.sudo().partner_shipping_pro_id = ticket_browse_id.partner_id.id
                            data.append(res_update)
                        else:
                            res_line = request.env['product.in.out.register.lines'].sudo().create({
                                'register_id': register_id.id,
                                'product_id': product_id.id,
                                'name': product_id.display_name,
                                'uom_id': product_id.uom_id.id,
                                'operation_type': 'out',
                                'partner_id': ticket_browse_id.partner_id.id,
                                'ticket_id': ticket_id,
                                'state': 'with_customer'
                            })
                            data.append(res_line)
            else:
                if not register_id:
                    for product in kw.get('product_ids', []):
                        product_id = request.env['product.product'].browse(int(product['product_id']))
                        vals = {
                            'product_id': product_id.id,
                            'name': product_id.display_name,
                            'uom_id': product_id.uom_id.id,
                            'operation_type': 'out',
                            'partner_id': partner_id,
                            'state': 'with_customer'
                        }
                        product_register.append((0, 0, vals))
                    res = request.env['product.in.out.register'].sudo().create({
                        'line_ids': product_register,
                        'assign_user': r_user.id,
                    })
                else:
                    for product in kw.get('product_ids', []):
                        product_id = request.env['product.product'].browse(int(product['product_id']))
                        line = register_id.line_ids.filtered(lambda i: i.product_id.id == product_id)
                        if line:
                            line.update({
                                'partner_id': partner_id,
                                'state': 'with_customer'

                            })
                        else:
                            res_line = request.env['product.in.out.register.lines'].sudo().create({
                                'register_id': register_id.id,
                                'product_id': product_id,
                                'name': product_id.diplay_name,
                                'uom_id': product_id.uom_id.id,
                                'operation_type': 'out',
                                'partner_id': partner_id,
                                'state': 'with_customer'
                            })
        except Exception as e:
            return {
                'code': 1001,
                'message': e,
                # 'data': [],
                # 'line_lis': []
            }

        return {
            'code': 1000,
            'message': 'Registration Deliver Successfully!',
            # 'data': vals,
            # 'records': register_length
        }

    @http.route('/web/in/out/register/receive', type='json', auth="user")
    def in_out_product_register_receive(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        r_user = request.env['res.users'].browse(uid)
        try:
            # product_id = int(kw.get('product_id', False))
            partner_id = int(kw.get('partner_id', False))
            assign_user_id = int(kw.get('assign_user', False))
            ticket_id = int(kw.get('ticket_id', False))
            # product_browse_id = request.env['product.product'].browse(product_id)
            ticket_browse_id = request.env['helpdesk.ticket'].browse(ticket_id)
            domain = [('date', '=', dateutil.utils.today()), ('assign_user', '=', r_user.id)]
            register_id = request.env['product.in.out.register'].sudo().search(domain, limit=1)
            product_register = []
            if ticket_id:
                if not register_id:
                    for product in kw.get('product_ids', []):
                        product_id = request.env['product.product'].browse(int(product['product_id']))
                        vals = {
                            'product_id': product_id.id,
                            'name': product_id.display_name,
                            'uom_id': product_id.uom_id.id,
                            'operation_type': 'in',
                            'partner_id': ticket_browse_id.partner_id.id,
                            'ticket_id': ticket_id,
                            'state': 'with_user'
                        }
                        product_register.append((0, 0, vals))
                    res = request.env['product.in.out.register'].sudo().create({
                        'line_ids': product_register,
                        'assign_user': r_user.id,
                    })
                else:
                    for product in kw.get('product_ids', []):
                        product_id = request.env['product.product'].browse(int(product['product_id']))
                        line = register_id.line_ids.filtered(lambda i: i.product_id.id == product_id)
                        if line:
                            line.update({
                                'partner_id': ticket_browse_id.partner_id.id,
                                'ticket_id': ticket_id,
                                'state': 'with_user'
                            })
                        else:
                            res_line = request.env['product.in.out.register.lines'].sudo().create({
                                'register_id': register_id.id,
                                'product_id': product_id.id,
                                'name': product_id.display_name,
                                'uom_id': product_id.uom_id.id,
                                'operation_type': 'in',
                                'partner_id': ticket_browse_id.partner_id.id,
                                'ticket_id': ticket_id,
                                'state': 'with_user'
                            })
            else:
                if not register_id:
                    for product in kw.get('product_ids', []):
                        product_id = request.env['product.product'].browse(int(product['product_id']))
                        vals = {
                            'product_id': product_id.id,
                            'name': product_id.diplay_name,
                            'uom_id': product_id.uom_id.id,
                            'operation_type': 'in',
                            'partner_id': partner_id,
                            'state': 'with_user'
                        }
                        product_register.append((0, 0, vals))
                    res = request.env['product.in.out.register'].sudo().create({
                        'line_ids': product_register,
                        'assign_user': r_user.id,
                    })
                else:
                    for product in kw.get('product_ids', []):
                        product_id = request.env['product.product'].browse(int(product['product_id']))
                        line = register_id.line_ids.filtered(lambda i: i.product_id.id == product_id)
                        if line:
                            line.update({
                                'partner_id': partner_id,
                                'state': 'with_user'
                            })
                        else:
                            res_line = request.env['product.in.out.register.lines'].sudo().create({
                                'register_id': register_id.id,
                                'product_id': product_id.id,
                                'name': product_id.display_name,
                                'uom_id': product_id.uom_id.id,
                                'operation_type': 'in',
                                'partner_id': partner_id,
                                'state': 'with_user'
                            })
        except Exception as e:
            return {
                'code': 1001,
                'message': e,
                # 'data': [],
                # 'line_lis': []
            }

        return {
            'code': 1000,
            'message': 'Registration Receive Successfully!',
            # 'data': vals,
            # 'records': register_length
        }

    @http.route('/web/in/out/register/validation', type='json', auth="user")
    def in_out_product_register_validation(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        try:
            prefix = 'C-'
            if prefix not in kw.get('default_code', False):
                default_code = prefix + kw.get('default_code', False)
            else:
                default_code = kw.get('default_code', False)
            product_id = request.env['product.product'].sudo().search([('default_code', '=', default_code)])
            ticket_id = int(kw.get('ticket_id', False))
            ticket_browse_id = request.env['helpdesk.ticket'].browse(ticket_id)
            current_date = fields.Date.today()
            # assign_user = int(kw.get('assign_user', False))
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            data = []
            if not product_id:
                return {
                    'code': 1001,
                    'message': '!! Product not Found !!',
                }

            if request.env.user.has_group('ki_contract_menu.group_smart_printer_service_engineer'):
                if ticket_id:
                    res = request.env['product.in.out.register.lines'].sudo().search(
                        [('operation_type', '=', 'out'), ('register_id.assign_user', '=', ticket_browse_id.user_id.id),
                         ('product_id.default_code', '=', default_code),('register_id.date','=',current_date)])
                    if res:
                        rec = request.env['product.product'].sudo().search(
                            [('default_code', '=', default_code)])
                        val = {
                            'name': rec.display_name,
                            'default_code': rec.default_code,
                            'image_url': base_url + '/web/image/product.product/%s/image_1920' % rec.id,
                            'product_id': {
                                'id': rec.id,
                                'name': rec.display_name,
                            },
                            'categ_id': {
                                'id': rec.categ_id.id,
                                'name': rec.categ_id.name
                            }
                        }
                        data.append(val)
                    else:
                        return {
                            'code': 1001,
                            'message': '!! Product not Found !!',
                        }
                else:
                    res = request.env['product.in.out.register.lines'].sudo().search(
                        [('operation_type', '=', 'out'),('register_id.date','=',current_date),
                         ('product_id.default_code', '=', default_code)])
                    if res:
                        rec = request.env['product.product'].sudo().search(
                            [('default_code', '=', default_code)])
                        val = {
                            'name': rec.display_name,
                            'default_code': rec.default_code,
                            'image_url': base_url + '/web/image/product.product/%s/image_1920' % rec.id,
                            'product_id': {
                                'id': rec.id,
                                'name': rec.display_name,
                            },
                            'categ_id': {
                                'id': rec.categ_id.id,
                                'name': rec.categ_id.name
                            }
                        }
                        data.append(val)
                    else:
                        return {
                            'code': 1001,
                            'message': '!! Product not Found !!',
                        }
            else:
                rec = request.env['product.product'].sudo().search(
                    [('default_code', '=', default_code)])
                val = {
                    'name': rec.display_name,
                    'default_code': rec.default_code,
                    'image_url': base_url + '/web/image/product.product/%s/image_1920' % rec.id,
                    'product_id': {
                        'id': rec.id,
                        'name': rec.display_name,
                    },
                    'categ_id': {
                        'id': rec.categ_id.id,
                        'name': rec.categ_id.name
                    }
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
            'message': 'Record Found Successfully!',
            'data': data
        }
