from odoo import http
from odoo.http import request


class SelectTicketType(http.Controller):

    @http.route('/ticket_type/', auth="public", type="json", methods=['POST'], website=True, csrf=False)
    def select_ticket_type(self, **_kwargs):
        ticket_id = _kwargs['ticket_type']
        ticket_data = []
        ticket = http.request.env['helpdesk.categories'].sudo().search([('id', '=', ticket_id)])

        for rec in ticket.helpdesk_types_ids:
            ticket_data.append(rec)
        return {
            'message': request.env['ir.ui.view']._render_template("cue_helpdesk.template_display_ticket_type", {
                'ticket': ticket_data,
            })
        }
