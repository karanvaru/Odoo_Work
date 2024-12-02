# -*- coding: utf-8 -*-
from odoo import http

# class RdpCustomerSupplierRmaExtended(http.Controller):
#     @http.route('/rdp_customer_supplier_rma_extended/rdp_customer_supplier_rma_extended/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rdp_customer_supplier_rma_extended/rdp_customer_supplier_rma_extended/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('rdp_customer_supplier_rma_extended.listing', {
#             'root': '/rdp_customer_supplier_rma_extended/rdp_customer_supplier_rma_extended',
#             'objects': http.request.env['rdp_customer_supplier_rma_extended.rdp_customer_supplier_rma_extended'].search([]),
#         })

#     @http.route('/rdp_customer_supplier_rma_extended/rdp_customer_supplier_rma_extended/objects/<model("rdp_customer_supplier_rma_extended.rdp_customer_supplier_rma_extended"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rdp_customer_supplier_rma_extended.object', {
#             'object': obj
#         })