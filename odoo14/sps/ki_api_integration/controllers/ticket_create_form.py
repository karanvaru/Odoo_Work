import base64
import json
import logging

from odoo import http, _, fields
from odoo.http import request, content_disposition

logger = logging.getLogger(__name__)


class TicketCreateForm(http.Controller):

    # Ticket Create
    @http.route('/web/ticket/create/form', type='http', auth="user", csrf=False)
    def create_ticket(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        ticket_cre = request.env['helpdesk.ticket'].sudo().search([])
        result = {
            'code': 1000,
            'message': 'Ticket Created Successfully!',
        }

        try:
            product_new_id = int(kw.get('product_id', False))
            if product_new_id == 0:
                result = {
                    'code': 200,
                    'message': 'Please add Product!',
                    'data': []
                }
                return json.dumps(result)

            else:
                product_id = request.env['product.product'].browse(product_new_id)

            contract_id = int(kw.get('contract_id', False))
            re = request.env['contract.contract'].sudo().search([('id', '=', contract_id)])
            if contract_id == 0 and product_id.categ_id.type == 'printer':
                result = {
                    'code': 200,
                    'message': 'Please add Contract Details!',
                    'data': []
                }
                return json.dumps(result)

            description = kw.get('description', False)
            if not description:
                result = {
                    'code': 200,
                    'message': 'Please add Description!',
                    'data': []
                }
                return json.dumps(result)

            category_id = int(kw.get('category_id', False))
            if category_id == 0:
                result = {
                    'code': 200,
                    'message': 'Please add Category',
                    'data': []
                }
                return json.dumps(result)

            stage_id = request.env['helpdesk.ticket.stage'].sudo().search([('name', '=', 'Assign')])
            date_time = fields.Datetime.now()
            user_id = request.env['res.users'].browse(uid)
            ticket_vals = ticket_cre.default_get(ticket_cre._fields)
            if request.env.user.has_group('ki_contract_menu.group_smart_printer_service_engineer'):
                ticket_line = []
                partner = False
                partner_name = False
                if kw.get('parts_line', []):
                    for rec in json.loads(kw.get('parts_line', [])):
                        vals = {
                            'product_id': rec['product_id'],
                            'quantity': rec['quantity'],
                        }
                        ticket_line.append((0, 0, vals))
                if re:
                    partner = re.partner_id.id
                    partner_name = re.partner_id.name
                else:
                    partner = product_id.customer_id.id
                    partner_name = product_id.customer_id.name
                ticket_vals.update({
                    'name': user_id.name,
                    'partner_id': partner,
                    'product_id': product_id.id,
                    'contract_id': contract_id,
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
                files = request.httprequest.files.getlist('files')
                for ufile in files:
                    request.env['ir.attachment'].sudo().create({
                        'name': ufile.filename,
                        'type': 'binary',
                        'datas': base64.encodebytes(ufile.read()),
                        'res_model': 'helpdesk.ticket',
                        'res_id': ticket_id.id
                    })

            else:
                partner = False
                partner_name = False
                ticket_line = []
                # if kw.get('parts_line'):
                if kw.get('parts_line', []):
                    for rec in json.loads(kw.get('parts_line', [])):
                        vals = {
                            'product_id': rec['product_id'],
                            'quantity': rec['quantity'],
                        }
                        ticket_line.append((0, 0, vals))
                if re:
                    partner = re.partner_id.id
                    partner_name = re.partner_id.name
                else:
                    partner = product_id.customer_id.id
                    partner_name = product_id.customer_id.name
                ticket_vals.update({
                    'name': user_id.name,
                    'partner_id': partner,
                    'product_id': product_id.id,
                    'contract_id': contract_id,
                    'description': description,
                    'partner_name': partner_name,
                    'category_id': category_id,
                    'ticket_line_ids': ticket_line,
                })
                ticket_id = ticket_cre.sudo().create(ticket_vals)
                ticket_id._onchange_contract_id()
                files = request.httprequest.files.getlist('files')
                for ufile in files:
                    request.env['ir.attachment'].sudo().create({
                        'name': ufile.filename,
                        'type': 'binary',
                        'datas': base64.encodebytes(ufile.read()),
                        'res_model': 'helpdesk.ticket',
                        'res_id': ticket_id.id
                    })

        except Exception as e:
            logger.exception("Fail to Create Ticket")
            result = {
                'code': 1001,
                'message': str(e)
            }

        return json.dumps(result)
