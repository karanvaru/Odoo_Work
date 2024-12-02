from odoo import http, _, fields
from odoo.http import request
from odoo.tools import float_repr, html2plaintext


class TicketDetails(http.Controller):

    @http.route('/web/ticket/details', type='json', auth="user")
    def ticket_details(self, **kw):
        state_label = {}
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
        r_user = request.env['res.users'].browse(uid)
        try:
            ticket_id = int(kw.get('ticket_id', False))
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            data = []
            register_ids = request.env['product.in.out.register'].sudo().search(
                [('line_ids.ticket_id', '=', ticket_id)])
            if ticket_id:
                if request.env.user.has_group(
                        'ki_contract_menu.group_smart_printer_admin') or request.env.user.has_group(
                    'ki_contract_menu.group_smart_printer_administrator'):
                    res = request.env['helpdesk.ticket'].sudo().search([('id', '=', ticket_id)])

                elif request.env.user.has_group(
                        'ki_contract_menu.group_smart_printer_customer_user'):
                    res = request.env['helpdesk.ticket'].sudo().search(
                        [('id', '=', ticket_id), ('create_uid', '=', r_user.id)])

                elif request.env.user.has_group(
                        'ki_contract_menu.group_smart_printer_service_engineer'):
                    res = request.env['helpdesk.ticket'].sudo().search(
                        [('id', '=', ticket_id), ('user_id', '=', r_user.id)])
                else:
                    return {
                        'code': 1000,
                        'message': 'You Are Not Able to Visit Ticket',
                        'data': []
                    }
                if res:
                    d = html2plaintext(res.description)
                    data = []
                    at_url = []
                    cartridge_lis = []
                    for a in res.attachment_ids:
                        a_url = base_url + "/web/content/?model=ir.attachment&id=" + str(
                            a.id) + "&filename_field=name&field=datas&download=true&name=" + a.name,
                        vals = {
                            'attachment_url': a_url,
                            'attachment_id': a.id,
                            'attachment_name': a.name,
                        }
                        at_url.append(vals)
                    for line in register_ids:
                        for cartridge in line.line_ids.filtered(lambda l: l.ticket_id.id == ticket_id):
                            # v = {
                            #     'product_id': cartridge.product_id.id,
                            #     'name': cartridge.product_id.display_name
                            # }
                            #
                            v = {
                                'id': cartridge.id,
                                'name': cartridge.name,
                                'product_id': {
                                    'id': cartridge.product_id.id,
                                    'name': cartridge.product_id.display_name
                                },
                                'uom_id': {
                                    'id': cartridge.uom_id.id,
                                    'name': cartridge.uom_id.name,
                                },
                                'quantity': cartridge.quantity,
                                'comment': cartridge.comment,
                                'operation_type': cartridge.operation_type,
                                'partner_id': {
                                    'id': cartridge.partner_id.id,
                                    'name': cartridge.partner_id.display_name,
                                },
                                # 'state':cartridge.state,
                                'state': state_label[cartridge.state],

                            }
                            cartridge_lis.append(v)
                    val = {
                        'ticket_id':res.id,
                        'number': res.number,
                        'name': res.create_uid.id,
                        'create_date': res.create_date,
                        'assigned_date': res.assigned_date,
                        'closed_date': res.closed_date,
                        'description': d,
                        'priority': res.priority,
                        'attachment': at_url,
                        'product_id': {
                            'id': res.product_id.id,
                            'model': res.product_id.name,
                            'asset_number': res.product_id.default_code,
                            'serial_number': res.product_id.barcode,
                        },
                        'customer_details': {
                            'id': res.create_uid.id,
                            'name': res.create_uid.name,
                            'phone': res.create_uid.work_phone,
                        },
                        'contract_id': {
                            'id': res.contract_id.id,
                            'name': res.contract_id.name,
                            'location': res.contract_id.partner_shipping_id.name,
                        },
                        'partner_id': {
                            'id': res.partner_id.id,
                            'name': res.partner_id.name,
                            'image_url': base_url + '/web/image/res.partner/%s/image_1920' % res.partner_id.id,
                        },
                        'user_id': {
                            'id': res.user_id.id,
                            'name': res.user_id.name,
                            'phone': res.user_id.work_phone,
                            # 'mobile': res.user_id.mobile,
                        },
                        'stage_id': {
                            'id': res.stage_id.id,
                            'name': res.stage_id.name
                        },
                        'category_id': {
                            'id': res.category_id.id,
                            'name': res.category_id.name,
                            'type': res.category_id.type,
                        },
                        'cartridge_list': cartridge_lis
                    }
                    data.append(val)
            else:
                return {
                    'code': 1000,
                    'message': '!!! Ticket not Found !!!',
                    'data': []
                }
        except Exception as e:
            return {
                'code': 100,
                'message': e,
                'data': []
            }

        return {
            'code': 1000,
            'message': 'Ticket Found Successfully!',
            'data': data
        }
