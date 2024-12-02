# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################
import werkzeug.utils
import werkzeug.wrappers
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)
from odoo import http, _
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.website_sale.controllers.main   import WebsiteSale


class ReferEarnSignup(AuthSignupHome):

	@http.route('/web/signup', type='http', auth='public', website=True)
	def web_auth_signup(self, *args, **kw):
		referral = request.httprequest.args.get('referral')
		result = super(ReferEarnSignup, self).web_auth_signup(*args, **kw)
		result.qcontext.update({
			'referral':referral
			})
		if result.qcontext.get('error'):
			return result
		else:
			user = request.env.user
			if request.httprequest.method == 'POST':
				if kw.get('referral'):
					checkparentReferral = user.partner_id._createReferralAccount(
						partner_id=user.partner_id.id,
						parent_referral_code=kw['referral'],
						user_id=user.id
						)
					if referral and referral == kw['referral']:
						user.partner_id.is_direct = False
					else:
						user.partner_id.is_direct = True

					if checkparentReferral['is_parent_referral']:
						request.env['transaction.history'].sudo()._createTransactionSignup(
							partner_id = user.partner_id.id,
							user_id = user.id,
							parent_user_id = checkparentReferral['parent_user_id']
							)
					else:
						request.env['transaction.history'].sudo()._createInvalidTransactionSignup(
							user_id = user.id,
							invalid_referal=kw.get('referral')
							)

				else:
					ReferralCustomer = user.partner_id._createReferralAccount(
						partner_id=user.partner_id.id,
						parent_referral_code="",
						user_id=user.id
						)
			return result


class ReferEarnWebsiteSale(WebsiteSale):

	@http.route(['/shop/confirmation'], type='http', auth="public", website=True)
	def payment_confirmation(self, **post):
		result = super(ReferEarnWebsiteSale, self).payment_confirmation(**post)
		user = request.env.user
		checkComsnType = request.env['res.config.settings'].sudo().get_values().get('verify_commission') == 'afterOrder'
		if checkComsnType and result.qcontext.get('order'):
			order = request.env['sale.order'].sudo().search([('partner_id','=',user.partner_id.id)])
			if len(order) == 1:
				TxnObj = request.env['transaction.history'].sudo()
				_logger.info("-----first order----------")
				if order.state == 'sale':
					_logger.info("----------check and give commissions------------")
					_logger.info("-----if--order.state-%r-----------", order.state)
					TxnObj.addComsnOnFirstSale(user_id=user.id,first_order=order.id)
					# addComsnOnFirstSale() this methods runs when payment gateway is used and
					# sale order is directly converted to state 'sale'
				else:
					_logger.info("-----else--order.state-%r-----------", order.state)
					TxnObj.addFirstOrderTransaction(user_id=user.id,first_order=order.id)


		return result


	@http.route('/shop/payment/validate', type='http', auth="public", website=True)
	def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
		""" Method that should be called by the server when receiving an update
		for a transaction. State at this point :

		 - UDPATE ME
		"""
		result = super(ReferEarnWebsiteSale,self).payment_validate(transaction_id, sale_order_id, **post)
		user = request.env.user
		last_saleOrder = user.partner_id.last_website_so_id
		if last_saleOrder.use_re_epoints and user.partner_id.referral_earning > 0.0:
			request.env['transaction.history'].sudo()._create_ReferaldebitTransaction(
				user_id=user.id ,
				amount=last_saleOrder.redeemable_points,
				order_id=last_saleOrder.id,
				order_name=last_saleOrder.name
				)
		return result
