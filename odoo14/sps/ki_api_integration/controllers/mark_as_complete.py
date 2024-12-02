from odoo import http, _, fields
from odoo.http import request
from datetime import datetime


class MarkAsDoneTicket(http.Controller):
    # Assign API
    @http.route('/web/done/ticket', type='json', auth="public")
    def action_ticket_mark_as_done(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        try:
            ticket_id = int(kw.get('ticket_id', False))
            ticket_com = request.env['helpdesk.ticket'].browse(ticket_id)
            ticket_msg = kw.get('comment', False)
            ticket_com.message_post(body=ticket_msg)
            for data in kw.get('files', []):
                request.env['ir.attachment'].create({
                    'name': data['name'],
                    'type': 'binary',
                    'datas': data['data'],
                    'res_model': 'helpdesk.ticket',
                    'res_id': ticket_id,
                })

            if not ticket_id:
                return {
                    'code': 100,
                    'message': 'Ticket Not Found!',
                    'data': []
                }

            stage = request.env['helpdesk.ticket.stage'].sudo().search([('name', '=', 'Done')])
            date_time = fields.Datetime.now()
            ticket_com.update({
                'stage_id': stage,
                'closed_date': date_time
            })

        except Exception as e:
            return {
                'code': 100,
                'message': e,
                'data': []
            }

        return {
            'code': 1000,
            'message': 'Tickets Done Successfully!',
            'data': [],
        }

