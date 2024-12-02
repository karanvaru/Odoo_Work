import logging
from odoo import http, SUPERUSER_ID, registry
from odoo.api import Environment
from werkzeug.exceptions import BadRequest

logger = logging.getLogger(__name__)


class AsteriskCallsController(http.Controller):

    @http.route('/asterisk_calls/signup', auth='user')
    def signup(self):
        # Used from About -> Support menu to signup by email for updates.
        user = http.request.env['res.users'].browse(http.request.uid)
        email = user.partner_id.email
        if not email:
            return http.request.render('asterisk_calls.email_not_set')
        else:
            mail = http.request.env['mail.mail'].create({
                'subject': 'Asterisk calls subscribe request',
                'email_from': email,
                'email_to': 'odooist@gmail.com',
                'body_html': '<p>Email: {}</p>'.format(email),
                'body': 'Email: {}'.format(email),
            })
            mail.send()
            return http.request.render('asterisk_calls.email_sent',
                                       qcontext={'email': email})
