from odoo import http, _
from odoo.http import request, Controller


class HelpdeskSupport(http.Controller):

    @http.route(['/contract_varification/<int:contract>'], type='http', auth="public", website=True)
    def email_verification(self, contract,):
        return request.render('reddot_commission.contract_verification', {'contract': contract})

    @http.route(['/contract_verification_data'], type='http', auth="public", website=True)
    def contract_verification_data(self, **post):
        contract_id = request.env['hr.contract'].sudo().search([('employee_id', '=', int(post['contract_val']))])
        if post['varify'] == "approve":
            contract_id.write({
                'contract_state': 'approve'
            })
        else:
            contract_id.write({
                'contract_state': 'reject'
            })
        return http.request.render('website.contactus_thanks')

