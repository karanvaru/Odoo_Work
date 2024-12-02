# -*- coding: utf-8 -*-
from odoo import http

# class CostEstimation(http.Controller):
#     @http.route('/cost_estimation/cost_estimation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cost_estimation/cost_estimation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cost_estimation.listing', {
#             'root': '/cost_estimation/cost_estimation',
#             'objects': http.request.env['cost_estimation.cost_estimation'].search([]),
#         })

#     @http.route('/cost_estimation/cost_estimation/objects/<model("cost_estimation.cost_estimation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cost_estimation.object', {
#             'object': obj
#         })