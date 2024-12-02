# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class CustomController(http.Controller):
    @http.route('/submit_form', type='http', auth='public', methods=['POST'], website=True)
    def submit_form(self, **post):
        if request.uid:  # Check if the user is logged in
            # Handle form submission
            field1 = post.get('field1')
            field2 = post.get('field2')
            # Process the form data here
            return request.render('reddot_wms.thank_you_template')
        else:
            # Redirect to login page if not logged in
            return request.redirect('/web/login')

    @http.route('/custom_form', type='http', auth='public', website=True)
    def display_form(self, **kw):
        return request.render('reddot_wms.custom_form_template')

#     @http.route('/reddot_wms/reddot_wms/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('reddot_wms.listing', {
#             'root': '/reddot_wms/reddot_wms',
#             'objects': http.request.env['reddot_wms.reddot_wms'].search([]),
#         })

#     @http.route('/reddot_wms/reddot_wms/objects/<model("reddot_wms.reddot_wms"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('reddot_wms.object', {
#             'object': obj
#         })
