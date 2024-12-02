# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################
from odoo import api, fields, models, _
from odoo import tools
from odoo.http import request
import logging
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
	_inherit = 'product.template'
	override_config = fields.Boolean('Override Default Configuration',help="By setting this true all the configuration values will be overriden.")
	delivery_to_use = fields.Selection([('default','Default Delivery Lead Time'),('advanced','Advanced Estimated Delivery')],'Compute Delivery Time By', default='default',required=True)
	zip_ranges = fields.One2many(comodel_name = 'available.pincodes', inverse_name = 'wk_product_template',string = 'Pincodes', help="Choose the range of the pincodes in which the product is available")

	@api.model
	def check_product_availability_in_pincode(self, pincode=False, product_id=False):
		flag = 0
		days = 0.0
		message = ''
		days_before = 0
		days_range = ''
		irDefault = self.env['ir.default'].sudo()
		available_message = irDefault.get('estimated.delivery.conf', 'available_message')
		unavailable_message = irDefault.get('estimated.delivery.conf', 'unavailable_message')
		display_mode =irDefault.get('estimated.delivery.conf', 'display_mode')
		add_days = irDefault.get('estimated.delivery.conf', 'add_days')
		number_of_days = irDefault.get('estimated.delivery.conf', 'number_of_days')
		if product_id:
			request.session['pincode'] = str(pincode)
			template_obj = self.browse(int(product_id))
			if template_obj.override_config:
				if template_obj.zip_ranges:
					for available_pincode_obj in template_obj.zip_ranges:
						pin_list = available_pincode_obj.pincodes
						for one_pincode in pin_list.split(","):  # search the pincode in the list of pincodes..
							one_pincode = one_pincode.strip()  # removes the spaces on either side
							if pincode == one_pincode:
								days = available_pincode_obj.delivered_within
								if display_mode == 'exact':
									message = '%s %s'%(available_message,days)
								else:
									if add_days == 'before':
										days_before = days - number_of_days
										days_range = '%s-%s days'%(int(days_before),int(days))
										message = '%s %s'%( available_message,days_range)
									else:
										days_after = days + number_of_days
										days_range = '%s-%s'%(int(days),int(days_after))
										message = '%s %s days'%( available_message,days_range)
								request.session['wk_days'] = days
								flag = 1
								break;
			else:
				zip_ids = self.env['ir.default'].sudo().get('estimated.delivery.conf', 'zip_ranges')
				if zip_ids:
					for zip_id in zip_ids:
						pincode_obj = self.env['available.pincodes'].browse(zip_id)
						pin_list = pincode_obj.pincodes
						for one_pincode in pin_list.split(","):  # search the pincode from configuration list..
							one_pincode = one_pincode.strip()  # removes the spaces on either side
							if pincode == one_pincode:
								days = pincode_obj.delivered_within
								if display_mode == 'exact':
									message = '%s %s'%(available_message,days)
								else:
									if add_days == 'before':
										days_before = days - number_of_days
										days_range = '%s-%s days'%(int(days_before),int(days))
										message = '%s %s'%( available_message,days_range)
									else:
										days_after = days + number_of_days
										days_range = '%s-%s days'%(int(days),int(days_after))
										message = '%s %s'%( available_message,days_range)
								request.session['wk_days'] = days
								flag = 1
								break;

		if flag == 1:
			return {'status':True,'message':message}
		else:
			message = '%s '%(unavailable_message)
			return {'status':False,'message':message}

	@api.model
	def _show_estimated_delivery(self):
		res = self.env['ir.default'].sudo().get('estimated.delivery.conf', 'show_estimated_delivery')
		return res
	
	@api.model
	def estimated_delivery_to_use(self , product_obj=False):
		if product_obj:
			if product_obj.override_config:
				return product_obj.delivery_to_use
			else:
				res = self.env['ir.default'].sudo().get('estimated.delivery.conf', 'delivery_to_use')
				return res
		return False

	@api.model
	def _get_default_message_to_show(self, product_obj=False):
		message = ''
		if product_obj:
			delivery_to_use = self.env['ir.default'].sudo().get('estimated.delivery.conf', 'delivery_to_use')
			delivery_message = self.env['ir.default'].sudo().get('estimated.delivery.conf', 'available_message')
			if delivery_to_use == 'default':
				message = '%s %s'%(delivery_message, product_obj.sale_delay)
			return message


class AvailablePincodes(models.Model):
	_name = 'available.pincodes'

	name = fields.Char('Name',required=True)
	pincodes = fields.Text('Comma Seperated Zipcodes', required=True, help="The product will be available in the following pincodes.The multiple pin codes should be seperated by comma(,)")
	delivered_within = fields.Float('Available Within',required=True, help="No of days within the product is available in given zipcode range")
	wk_product_template = fields.Many2one('product.template', 'Product Template')


class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'
 
	delivery_message_lines = fields.Char('Message')

	def show_estiamted_delivery_values_in_cart_lines(self, temp_id=False, order_id=False):
		delivery_to_use = ''
		final_message = ''
		status = ''
		pincode = ''
		if temp_id:
			if order_id:
				sale_order_obj = self.env['sale.order'].browse(int(order_id))
			template_obj = self.env['product.template'].sudo().browse(temp_id)
			irDefault = self.env['ir.default'].sudo()
			available_message = irDefault.get('estimated.delivery.conf', 'available_message')
			unavailable_message = irDefault.get('estimated.delivery.conf', 'unavailable_message')
			display_mode = irDefault.get('estimated.delivery.conf', 'display_mode')
			add_days = irDefault.get('estimated.delivery.conf', 'add_days')
			number_of_days = irDefault.get('estimated.delivery.conf', 'number_of_days')
			if template_obj.override_config:
				delivery_to_use = template_obj.delivery_to_use
			else:
				delivery_to_use = irDefault.get('estimated.delivery.conf', 'delivery_to_use')
			if delivery_to_use == 'default':
				if template_obj.sale_delay:
					if display_mode == 'exact':
						final_message = '%s %s'%( available_message,template_obj.sale_delay)
					else:
						if add_days == 'before':
							days_before = template_obj.sale_delay - number_of_days
							days_range = '%s-%s days'%(int(days_before),int(template_obj.sale_delay))
							final_message = '%s %s'%( available_message,days_range)
						else:
							days_after = template_obj.sale_delay + number_of_days
							days_range = '%s-%s days'%(int(template_obj.sale_delay),int(days_after))
							final_message = '%s %s'%( available_message,days_range)
					status = 'available'
				else:
					final_message = unavailable_message
					status = 'unavailable'
			else:
				if request.session.get('pincode'):
					pincode = request.session.get('pincode')
				else:
					if sale_order_obj and sale_order_obj.partner_id:
						partner_obj = self.env['res.partner'].browse(sale_order_obj.partner_id.id)
						pincode = partner_obj.partner_pincode
				if pincode:
					res = template_obj.check_product_availability_in_pincode(pincode, int(temp_id))
					if res:
						if res['status']:
							final_message = '%s'%(res['message'])
							status = 'available'
						else:
							final_message = unavailable_message
							status = 'unavailable'
				else:
					final_message = 'EnterPincode'
					status = 'none'
		return {'final_message':final_message,
				'status' : status
		}

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	order_pincode = fields.Char(string='Pincode')

	def show_estimated_delivery_in_cart_lines(self):
		ir_values = self.env['ir.default'].sudo().get('estimated.delivery.conf', 'show_delivery_in_cart')
		return ir_values

	def _get_order_lines_list(self, order_lines):
		order_line_list = []
		if order_lines:
			for order_line in order_lines:
				order_line_list.append(order_line.id)
		return order_line_list

	@api.model
	def show_advanced_delivery_cart(self):
		type_used = self.env['ir.default'].sudo().get('estimated.delivery.conf', 'delivery_to_use')
		return type_used





