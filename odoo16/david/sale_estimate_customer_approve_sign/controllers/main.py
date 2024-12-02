# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, http, _
from datetime import datetime
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
import binascii
from odoo.addons.sale_estimate_customer_portal.controllers.main import CustomerPortal


class CustomerPortal(CustomerPortal):

    @http.route(['/my/sale_estimate/custom/<int:estimate_id>'], type='http', auth="user", website=True)
    def portal_my_sale_estimate_form_custom(self,estimate_id,access_token=None, **kw):
        access_token = access_token or request.httprequest.args.get('access_token')
        estimate = request.env['sale.estimate'].sudo().browse(estimate_id)
        partner = request.env.user.partner_id
        if estimate.partner_id.commercial_partner_id.id and partner.commercial_partner_id.id != estimate.partner_id.commercial_partner_id.id:
           return request.redirect("/my")
        try:
            estimate_sudo = self._document_check_access('sale.estimate', estimate_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = {
        'estimate': estimate,
        }
        return request.render("sale_estimate_customer_approve_sign.portal_my_sale_estimate_form_custom", values)


    @http.route(['/my/sale_estimate/<int:estimate_id>/accept'], type='json', auth="public", website=True)
    def portal_timesheet_accept_custom(self, estimate_id, access_token=None, name=None, signature=None):
        access_token = access_token or request.httprequest.args.get('access_token')
        estimate_obj = request.env['sale.estimate']
        estimate_sudo = estimate_obj.sudo().browse(estimate_id)
        try:
            estimate_sudo.sudo().write({
                'custom_signed_by': name,
                'custom_signed_on': fields.Datetime.now(),
                'custom_signature': signature,
            })
            request.env.cr.commit()
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}


        query_string = '&message=sign_ok'
        return {
            'force_refresh': True,
        }

   