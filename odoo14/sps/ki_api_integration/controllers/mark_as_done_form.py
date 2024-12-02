import base64
import json
import logging

from odoo import http, _, fields
from odoo.http import request, content_disposition

logger = logging.getLogger(__name__)


class MarkAsDoneForm(http.Controller):

    # Ticket Create
    @http.route('/web/mark/done/form', type='http', auth="user", csrf=False)
    def ticket_mark_done(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        result = {
            'code': 1000,
            'message': 'Ticket Done Successfully!',
        }
        try:
            ticket_new_id = int(kw.get('ticket_id', False))
            ticket_id = request.env['helpdesk.ticket'].browse(ticket_new_id)
            if not ticket_id:
                result = {
                    'code': 200,
                    'message': 'Please add Ticket!',
                    'data': []
                }
                return json.dumps(result)
            comment = kw.get('comment', False)
            ticket_id.message_post(body=comment)

            files = request.httprequest.files.getlist('files')
            for ufile in files:
                request.env['ir.attachment'].sudo().create({
                    'name': ufile.filename,
                    'type': 'binary',
                    'datas': base64.encodebytes(ufile.read()),
                    'res_model': 'helpdesk.ticket',
                    'res_id': ticket_new_id
                })
            stage = request.env['helpdesk.ticket.stage'].sudo().search([('name', '=', 'Done')])
            date_time = fields.Datetime.now()
            ticket_id.update({
                'stage_id': stage,
                'closed_date': date_time
            })

        except Exception as e:
            logger.exception("Fail to Done Ticket")
            result = {
                'code': 1001,
                'message': str(e)
            }

        return json.dumps(result)





