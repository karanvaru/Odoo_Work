# -*- coding: utf-8 -*-

from odoo.http import request, route
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortalNew(CustomerPortal):

    if 'city' in CustomerPortal.MANDATORY_BILLING_FIELDS: 
        CustomerPortal.MANDATORY_BILLING_FIELDS.remove("city")
    
    if 'country_id' in CustomerPortal.MANDATORY_BILLING_FIELDS: 
        CustomerPortal.MANDATORY_BILLING_FIELDS.remove("country_id")

    if 'street' in CustomerPortal.MANDATORY_BILLING_FIELDS: 
        CustomerPortal.MANDATORY_BILLING_FIELDS.remove("street")


    @route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        return request.redirect('/my/account')
