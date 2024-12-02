from odoo import http
from odoo.http import request


class HelpDeskTickets(http.Controller):
    @http.route(['/help/tickets'], type="json", auth="user")
    def elearning_snippet(self):
        tickets = []
        help_tickets = request.env['helpdesk.support'].sudo().search(
            [('stage_id.stage_type', '=', 'new')])
        for i in help_tickets:
            tickets.append(
                {'name': i.name, 'subject': i.subject, 'id': i.id})
        values = {
            'h_tickets': tickets
        }
        response = http.Response(
            template='ki_helpdesk_dashboard.dashboard_tickets',
            qcontext=values)
        return response.render()
