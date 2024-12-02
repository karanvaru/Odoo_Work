from odoo import http, _, fields
from odoo.http import request


class TicketCreate(http.Controller):

    # Ticket Create
    @http.route('/web/ticket/create', type='json', auth="user")
    def create_ticket(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        ticket_cre = request.env['helpdesk.ticket'].sudo().search([])
        try:

            product_new_id = int(kw.get('product_id', False))
            if not product_new_id:
                return {
                    'code': 200,
                    'message': 'Please add Product!',
                    'data': []
                }
            else:
                product_id = request.env['product.product'].browse(product_new_id)

            contract_id = int(kw.get('contract_id', False))
            re = request.env['contract.contract'].sudo().search([('id', '=', contract_id)])
            if not contract_id and product_id.categ_id.type == 'printer':
                return {
                    'code': 200,
                    'message': 'Please add Contract Details!',
                    'data': []
                }

            # name = kw.get('name', False)
            # if not name:
            #     return {
            #         'code': 10002,
            #         'message': 'Please add Problem!',
            #         'data': []
            #     }
            description = kw.get('description', False)
            if not description:
                return {
                    'code': 200,
                    'message': 'Please add Description!',
                    'data': []
                }
            category_id = int(kw.get('category_id', False))
            if not category_id:
                return {
                    'code': 200,
                    'message': 'Please add Category',
                    'data': []
                }
            stage_id = request.env['helpdesk.ticket.stage'].sudo().search([('name', '=', 'Assign')])
            date_time = fields.Datetime.now()
            user_id = request.env['res.users'].browse(uid)
            ticket_vals = ticket_cre.default_get(ticket_cre._fields)
            if request.env.user.has_group('ki_contract_menu.group_smart_printer_service_engineer'):
                ticket_line = []
                partner = False
                partner_name = False
                department = False
                location = False
                for rec in kw.get('parts_line', []):
                    vals = {
                        'product_id': rec['product_id'],
                        'quantity': rec['quantity'],
                    }
                    ticket_line.append((0, 0, vals))
                if re:
                    partner = re.partner_id.id
                    partner_name = re.partner_id.name
                    # department = re.contract_line_fixed_ids.filtered(lambda line: line.product_id == product_id).department
                    # location = re.partner_shipping_id.id
                else:
                    partner = product_id.customer_id.id
                    partner_name = product_id.customer_id.name
                ticket_vals.update({
                    'name': user_id.name,
                    'mobile_number': user_id.work_phone,
                    'partner_id': partner,
                    'product_id': product_id.id,
                    'contract_id': contract_id,
                    # 'department': department,
                    # 'location_id': location,
                    'description': description,
                    'user_id': user_id.id,
                    'partner_name': partner_name,
                    'category_id': category_id,
                    'stage_id': stage_id.id,
                    'assigned_date': date_time,
                    'ticket_line_ids': ticket_line,
                })
                ticket_id = ticket_cre.sudo().create(ticket_vals)
                ticket_id._onchange_contract_id()
                for data in kw.get('files', []):
                    request.env['ir.attachment'].sudo().create({
                        'name': data['image'],
                        'type': 'binary',
                        'datas': data['data'],
                        'res_model': 'helpdesk.ticket',
                        'res_id': ticket_id.id
                    })
            else:
                partner = False
                partner_name = False
                department = False
                location = False
                ticket_line = []
                for rec in kw.get('parts_line', []):
                    vals = {
                        'product_id': rec['product_id'],
                        'quantity': rec['quantity'],
                    }
                    ticket_line.append((0, 0, vals))
                if re:
                    partner = re.partner_id.id
                    partner_name = re.partner_id.name
                    # department = re.contract_line_fixed_ids.filtered(lambda line: line.product_id == product_id).department
                    # location = re.partner_shipping_id.id

                else:
                    partner = product_id.customer_id.id
                    partner_name = product_id.customer_id.name
                ticket_vals.update({
                    'name': user_id.name,
                    'mobile_number': user_id.work_phone,
                    'partner_id': partner,
                    'product_id': product_id.id,
                    # 'department': department,
                    # 'location_id': location,
                    'contract_id': contract_id,
                    'description': description,
                    'partner_name': partner_name,
                    'category_id': category_id,
                    'ticket_line_ids': ticket_line,
                })
                ticket_id = ticket_cre.sudo().create(ticket_vals)
                ticket_id._onchange_contract_id()

                for data in kw.get('files', []):
                    request.env['ir.attachment'].sudo().create({
                        'name': data['image'],
                        'type': 'binary',
                        'datas': data['data'],
                        'res_model': 'helpdesk.ticket',
                        'res_id': ticket_id.id
                    })
                    # request.env['helpdesk.ticket.line'].sudo().create({
                    #     'product_id': rec.product_id.id,
                    #     'quantity': rec.quantity,
                    # })
        except Exception as e:
            return {
                'code': 1001,
                'message': e,
                'data': []
            }
        return {
            'code': 1000,
            'message': 'Ticket Created Successfully!',
        }
