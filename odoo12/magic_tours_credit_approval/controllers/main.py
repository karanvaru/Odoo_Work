# -*- coding: utf-8 -*-

from odoo.http import request
from odoo import http, _
import logging
from odoo.exceptions import AccessDenied, AccessError, MissingError, UserError, ValidationError

_logger = logging.getLogger(__name__)

from odoo import fields, http, SUPERUSER_ID, tools, _
# from odoo.fields import Command
from odoo.http import content_disposition, Controller, request, route
from odoo.addons.portal.controllers.portal import pager as portal_pager


class CreditApproval(http.Controller):
    # MANDATORY_BILLING_FIELDS = ["name", "phone", "email", "street", "city", "country_id"]
    # OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name"]

    
    @http.route('/credit_approval', type='http', auth="user", website=True, csrf=False)
    def fe_webform(self, **kw):
        ca_rec = request.env['credit.approval'].sudo().search([])
        return http.request.render('magic_tours_credit_approval.credit_approval', {
                                                                  'fe_rec': ca_rec})

    @http.route('/credit/creation', type="http", auth="user", website=True, csrf=False)
    def create_web_credit_approval(self, **kw):
        print("Data Received.....", kw)
        f_ls=request.env['credit.approval'].sudo().search([])
        ca_val = {
            'name':kw.get('name'),
            'credit_amount':kw.get('credit_amount'),
            'description':kw.get('description'),
            
        }
        
        res = f_ls.create(ca_val)
        return request.render("magic_tours_credit_approval.credit_thanks", {'gf_val':res})