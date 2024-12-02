from odoo import http, _, fields
from odoo.http import request

class TicketComment(http.Controller):

    @http.route('/web/ticket/comment', type='json', auth="user")
    def comment_ticket(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        try:
            ticket_id = int((kw.get('ticket_id', False)))
            ticket_com = request.env['helpdesk.ticket'].browse(ticket_id)
            ticket_msg = kw.get('comment', False)
            ticket_com.message_post(body=ticket_msg)
            for data in kw.get('files', []):
                request.env['ir.attachment'].create({
                    'name': data['name'],
                    'type': 'binary',
                    'datas': data['data'],
                    'res_model': 'helpdesk.ticket',
                    'res_id': ticket_id
                })
        except Exception as e:
            return {
                'code': 1001,
                'message': e,
                'data': []
            }
        return {
            'code': 1000,
            'message': 'Message Submitted Successfully!',
        }