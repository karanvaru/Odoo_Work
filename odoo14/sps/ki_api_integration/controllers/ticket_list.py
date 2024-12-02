from odoo import http, _, fields
from odoo.http import request
from odoo.tools import float_repr, html2plaintext


class TicketList(http.Controller):

    @http.route('/web/ticket/list', type='json', auth="user")
    def ticket_list(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        res = request.env['res.users'].browse(uid)
        try:
            url_params = request.httprequest.args.to_dict()
            start = int(url_params.get('start', 0))
            end = int(url_params.get('end', 0))
            limit = end + 1 - start
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if limit < 1:
                limit = 10
            ticket_ls = False
            stage_id = int(kw.get('stage_id', False))
            category_id = int(kw.get('category_id', False))
            number = kw.get('number', False)
            number_domain = []
            stage_domain = []
            category_domain = []
            if stage_id:
                stage_domain = [('stage_id', '=', stage_id)]
            if category_id:
                category_domain = [('category_id', '=', category_id)]
            if number and number != '':
                number_domain = [('number', '=', number)]
            if request.env.user.has_group('ki_contract_menu.group_smart_printer_service_engineer'):
                ticket_ls = request.env['helpdesk.ticket'].sudo().search(
                    [('user_id', '=', res.id)] + stage_domain + category_domain + number_domain,
                    limit=limit,
                    offset=start)
                ticket_length = request.env['helpdesk.ticket'].search_count(
                    [('user_id', '=', res.id)] + stage_domain + category_domain + number_domain)

            elif request.env.user.has_group('ki_contract_menu.group_smart_printer_admin') or request.env.user.has_group(
                    'ki_contract_menu.group_smart_printer_administrator'):
                ticket_ls = request.env['helpdesk.ticket'].sudo().search(
                    [] + stage_domain + category_domain + number_domain,
                    limit=limit,
                    offset=start)
                ticket_length = request.env['helpdesk.ticket'].search_count(
                    [] + stage_domain + category_domain + number_domain)

            elif request.env.user.has_group('ki_contract_menu.group_smart_printer_customer_user') or \
                    request.env.user.has_group('ki_contract_menu.group_smart_printer_owner'):
                # domain = [('contract_id', '!=', False),
                #           ('contract_id.partner_shipping_id.parent_id', 'child_of',
                #            res.partner_id.parent_id.id)]
                domain = [('create_uid', '=', res.id)] + stage_domain + category_domain
                ticket_ls = request.env['helpdesk.ticket'].sudo().search(domain, limit=limit, offset=start)
                ticket_length = request.env['helpdesk.ticket'].search_count(domain)

            if not ticket_ls:
                return {
                    'code': 100,
                    'message': 'Ticket Not Found!',
                    'data': []
                }
            data = []
            for rec in ticket_ls:
                d = html2plaintext(rec.description)
                vals = {
                    'id': rec.id,
                    'name': rec.name,
                    'number': rec.number,
                    'create_date': rec.create_date,
                    'partner': rec.partner_name,
                    'description': d,
                    'priority': rec.priority,
                    'product_id': {
                        'id': rec.product_id.id,
                        'name': rec.product_id.name,
                    },
                    'contract_id': {
                        'id': rec.contract_id.id,
                        'name': rec.contract_id.name,
                    },
                    'partner_id': {
                        'id': rec.partner_id.id,
                        'name': rec.partner_id.name,
                        'image_url': base_url + '/web/image/res.partner/%s/image_1920' % rec.partner_id.id,
                    },
                    'stage_id': {
                        'name': rec.stage_id.name,
                    }
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
            'message': 'Tickets Found Successfully!',
            'data': data,
            'records': ticket_length
        }
