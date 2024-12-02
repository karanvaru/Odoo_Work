from datetime import datetime
from odoo import http, _, fields
from odoo.http import request

class AcceptTicket(http.Controller):
    # Assign API
    @http.route('/web/accept/ticket', type='json', auth="public")
    def action_ticket_assign(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        try:
            ticket_id = int(kw.get('ticket_id', False))
            if not ticket_id:
                return {
                    'code': 100,
                    'message': 'Ticket Not Found!',
                    'data': []
                }
            stage = request.env['helpdesk.ticket.stage'].sudo().search([('name', '=', 'In Progress')])
            res = request.env['helpdesk.ticket'].sudo().browse(ticket_id)
            date_time = fields.Datetime.now()
            res.update({
                'stage_id': stage,
                'assigned_date': date_time
            })

        except Exception as e:
            return {
                'code': 100,
                'message': e,
                'data': []
            }
        # device_id = "dz8bxOW7Tc21KRAMtXtt7X:APA91bFJYB8lRrzi232UOidFSwiCK3FjE6KD6spLoKuIavVjm5F72EbdOadYZhA4vYfxdn8KdfrNlP1esDvV-IfNpNkSI1GLU0xWrFwuscb_l3bC8g_L6TzIf9TJeWTxnyD5RbHWikd6"
        # if device_id:
        #     mobile_device_id = str(device_id),
        #     body = 'Ticket is Assigned.',
        #     title = 'Hey! You have new Assignment',
        # else:
        #     notif_status = "No Device Id Found"
        return {
            'code': 1000,
            'message': 'Tickets Accept Successfully!',
            'data': [],
            # 'notif_status': notif_status
        }


class RejectTicket(http.Controller):

    # Assign API
    @http.route('/web/reject/ticket', type='json', auth="public")
    def action_ticket_reject(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        try:
            ticket_id = int(kw.get('ticket_id', False))
            if not ticket_id:
                return {
                    'code': 100,
                    'message': 'Ticket Not Found!',
                    'data': []
                }
            stage = request.env['helpdesk.ticket.stage'].sudo().search([('name', '=', 'New')])
            res = request.env['helpdesk.ticket'].sudo().browse(ticket_id)
            res.update({
                'stage_id': stage,
                'user_id': False
            })

        except Exception as e:
            return {
                'code': 100,
                'message': e,
                'data': []
            }

        return {
            'code': 1000,
            'message': 'Tickets Rejected !!',
            'data': [],
            # 'records': ticket_length
        }
