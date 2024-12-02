from odoo import http, _
from odoo.http import request, Controller


class HelpdeskSupport(http.Controller):

    @http.route(['/structure_varification/<int:structure>'], type='http', auth="public", website=True)
    def email_verification(self, structure,):
        return request.render('reddot_commission.structure_verification', {'structure': structure})

    @http.route(['/structure_verification_data'], type='http', auth="public", website=True)
    def structure_verification_data(self, **post):
        structure_id = request.env['commission.structure'].sudo().search([('id', '=', int(post['structure_val']))])
        if post['varify'] == "approve":
            structure_id.write({
                'state': 'approved'
            })
        else:
            structure_id.write({
                'state': 'rejected'
            })
        return http.request.render('website.contactus_thanks')
