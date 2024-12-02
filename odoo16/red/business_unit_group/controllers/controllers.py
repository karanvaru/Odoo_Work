# -*- coding: utf-8 -*-
# from odoo import http


# class BusinessUnitGroup(http.Controller):
#     @http.route('/business_unit_group/business_unit_group', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/business_unit_group/business_unit_group/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('business_unit_group.listing', {
#             'root': '/business_unit_group/business_unit_group',
#             'objects': http.request.env['business_unit_group.business_unit_group'].search([]),
#         })

#     @http.route('/business_unit_group/business_unit_group/objects/<model("business_unit_group.business_unit_group"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('business_unit_group.object', {
#             'object': obj
#         })
