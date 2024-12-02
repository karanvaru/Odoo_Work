# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################
from odoo import http
from odoo.http import request
from odoo import SUPERUSER_ID
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging
_logger = logging.getLogger(__name__)

class WebsiteSale(WebsiteSale):
	@http.route(['/website/check/pincode'], type='json', auth="public", website=True)
	def check_pincode(self, pincode=False, template_id=False):
		if pincode and template_id:
			res = request.env['product.template'].sudo().check_product_availability_in_pincode(pincode,int(template_id))
			return res
		else:
			return False

	@http.route(['/website/change/pincode'],type='json', auth="public", website=True)
	def change_pincode(self, template_id=False):
		res = {}
		pincode = request.session.get('pincode')
		if pincode and template_id:
			res = request.env['product.template'].sudo().check_product_availability_in_pincode(pincode,int(template_id))
			return res
		else:
			return False

	@http.route(['/website/cart/pincode'],type='json', auth="public", website=True)
	def website_cart_pincode(self, order_id=False):
		pincode = request.session.get('pincode')
		sale_order_obj = request.env['sale.order'].browse(int(order_id))
		if pincode:
			return pincode
		elif sale_order_obj.partner_id:
			partner_obj = request.env['res.partner'].sudo().browse(sale_order_obj.partner_id.id)
			if partner_obj.partner_pincode:
				return sale_order_obj.partner_pincode
		else:
			return False

	@http.route(['/website/check/pincode/cart'],type='json', auth="public", website=True)
	def check_pincode_cart(self, pincode=False, order_id=False):
		if pincode:
			sale_order_obj = request.env['sale.order'].browse(int(order_id))
			request.session['pincode'] = pincode
			if sale_order_obj.partner_id:
				partner_obj = request.env['res.partner'].sudo().browse(sale_order_obj.partner_id.id)
				partner_obj.write({'partner_pincode':pincode})
				pincode = request.session.get('pincode')
				return pincode
		return False

	@http.route(['/website/check/pincode/cart/message'],type='json', auth="public", website=True)
	def check_pincode_cart_message(self, pincode=False, order_line_id=False):
		if order_line_id:
			line_obj = request.env['sale.order.line'].browse(int(order_line_id))
			template_id = line_obj.product_id.product_tmpl_id.id
			message = line_obj.show_estiamted_delivery_values_in_cart_lines(template_id, line_obj.order_id.id)
			return message
		return False
