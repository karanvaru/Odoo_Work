# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii

from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError, ValidationError
# from odoo.fields import Command
from odoo.http import request

from odoo.addons.payment.controllers import portal as payment_portal
# from odoo.addons.payment import utils as payment_utils
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.portal.controllers.portal import CustomerPortal, pager



class CustomerPortal(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        res = super(CustomerPortal,self)._prepare_home_portal_values(counters)
        print('RESULT',res)
        res['credit_count']= request.env['credit.approval'].search_count([])
        return res
    
    @http.route(['/my/credits','/my/credits/page/<int:page>'], type='http', auth="user", website=True)
    def _credit_portal_list_view(self,page=1,**kw):

        print('Controller Calling')
        credit_obj = request.env['credit.approval']
        total_credits = credit_obj.search_count([],limit=10,offset=page_details['offset'])
        credits= credit_obj.search([])
        page_details = pager(url='/my/credits',
                             total=total_credits,
                             page = page,
                             step=10
                             )
        vals = {
            'credits':credits,
            'page_name': 'credit_list_view_portal',
            'pager':page_details
        }  

        return request.render("magic_tours_credit_approval.credit_list_view_portal",vals)
    

    @http.route(['/my/credit/<model("credit.approval"):credit_id>'],type="http",website=True)
    def _credit_portal_form_view(self,credit_id, **kw):
        vals = {
            "credit":credit_id,
             'page_name': 'credit_form_view_portal'

        }
        credit_records = request.env['credit.approval'].search([])
        credit_ids = credit_records.ids
        credit_index = credit_ids.index(credit_id.id)
        if credit_index !=0 and credit_records[credit_ids[credit_index-1]] :
            vals['prev_record'] = 'my/credit/{}'.format(credit_ids[credit_index-1])
        if credit_index < len(credit_ids)-1 and credit_ids[credit_index+1]:
            vals['next_record'] = 'my/credit/{}'.format(credit_ids[credit_index+1])

        return request.render("magic_tours_credit_approval.credit_form_view_portal",vals)


    