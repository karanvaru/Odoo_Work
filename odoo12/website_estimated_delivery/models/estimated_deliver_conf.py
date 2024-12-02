# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################
from odoo import api, fields, models, _
from odoo import tools
import logging
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
_logger = logging.getLogger(__name__)

class EstimatedDeliveryConf(models.TransientModel):
	
	_name = 'estimated.delivery.conf'
	_inherit = 'webkul.website.addons'


	show_estimated_delivery = fields.Boolean('Show Delivery Time In Product', help="enable of disable the Estimated delivery in product page")
	show_delivery_in_cart = fields.Boolean('Show Delivery Time in Cart',help=" enable or disable the estimated delivery in the cart page")
	delivery_to_use = fields.Selection([('default','Default Delivery Lead Time'),('advanced','Advanced Estimated Delivery')],'Compute Delivery Time Using:', default='default', help="the delivery time will be calculated on the basis of default method or advanced method.",required=True)
	display_mode = fields.Selection([('exact','Exact'),('range','Range')],'Display Mode:', default='exact', help="display the mode of delivery to be used",required=True)
	add_days = fields.Selection([('before','Add Days Before'),('after','Add Days After')],'Create Delivery Day Range ', default='before', help="Add the number of days beore or after the actual delivery days in order to create the time range for delivery.On selecting 'Add Days Before' the number of days will be subtracted from the actual days and vice-versa")
	number_of_days = fields.Integer('Number of days', help="the number of days that will be added or subtrated the actual days in order to create a delivery range")
	zip_ranges = fields.Many2many('available.pincodes', 'conf_zipcodes_rel', 'conf_id','pincodes_id', string = 'Zipcodes', help="Choose the range of the pincodes in which the product is available")
	unavailable_message = fields.Char('Message To Display When product is Unavailable',translate=True, required=True, help="message to display when the product is unavailable in any location",)
	available_message = fields.Char('Message To Display When product is Available', translate=True, required=True, help="Message to display when the product is available in any location. The number of days will be added in last automatically")

	@api.multi
	def set_values(self):
		super(EstimatedDeliveryConf, self).set_values()
		IrDefault = self.env['ir.default'].sudo()
		IrDefault.set('estimated.delivery.conf','show_estimated_delivery', self.show_estimated_delivery)
		IrDefault.set('estimated.delivery.conf','delivery_to_use', self.delivery_to_use)
		IrDefault.set('estimated.delivery.conf','zip_ranges', self.zip_ranges.ids)
		IrDefault.set('estimated.delivery.conf','show_delivery_in_cart', self.show_delivery_in_cart)
		IrDefault.set('estimated.delivery.conf','unavailable_message', self.unavailable_message)
		IrDefault.set('estimated.delivery.conf','available_message', self.available_message)
		IrDefault.set('estimated.delivery.conf','display_mode', self.display_mode)
		IrDefault.set('estimated.delivery.conf','add_days', self.add_days)
		IrDefault.set('estimated.delivery.conf','number_of_days', self.number_of_days)
		return True

	@api.multi
	def get_values(self):
		res = super(EstimatedDeliveryConf, self).get_values()
		IrDefault = self.env['ir.default'].sudo()
		res.update({
			'show_estimated_delivery':IrDefault.get('estimated.delivery.conf','show_estimated_delivery'),
			'delivery_to_use':IrDefault.get('estimated.delivery.conf','delivery_to_use'),
			'zip_ranges':IrDefault.get('estimated.delivery.conf','zip_ranges'),
			'show_delivery_in_cart':IrDefault.get('estimated.delivery.conf','show_delivery_in_cart'),
			'unavailable_message':IrDefault.get('estimated.delivery.conf','unavailable_message'),
			'available_message':IrDefault.get('estimated.delivery.conf','available_message'),
			'display_mode':IrDefault.get('estimated.delivery.conf','display_mode'),
			'add_days':IrDefault.get('estimated.delivery.conf','add_days'),
			'number_of_days':IrDefault.get('estimated.delivery.conf','number_of_days'),
			
		})
		return res
	
