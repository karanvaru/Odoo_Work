from odoo import http, tools, _
from odoo.http import request
import requests


class SignUpPage(http.Controller):

    @http.route('/signup_mail', type='json', auth='public')
    def signup_mail(self, **kw):
        user_enter_email = kw.get('user_email')
        QueryString = kw.get('QueryString')
        company_name = request.env.company.name

        email_values = {
            'email_to': user_enter_email,
            'company_name': company_name,
            'QueryString': QueryString,
        }
        company_id = request.env.company.id
        mail_template = request.env.ref('cue_website_profile.signup_page_url_template').sudo()
        mail_template.with_context(email_values).send_mail(company_id, email_values=None, force_send=True)
        return 'success'
