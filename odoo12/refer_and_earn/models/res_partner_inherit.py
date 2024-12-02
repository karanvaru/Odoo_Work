# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
from odoo import models, fields,api,_
import random, string
import datetime
class ResPartnerInherit(models.Model):

	_inherit = 'res.partner'



	@api.multi
	def open_transactions(self):
		if self.user_ids:
			return {
				'type': 'ir.actions.act_window',
				'name': 'Referral Transaction',
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'transaction.history',
				'domain': [('user_id','=', self.user_ids[0].id)],
				'target': 'current',
			}
		else:
			raise UserError("There is no Transactions for this customer")




	referral_code = fields.Char(string = "Referral Code" ,readonly="1")
	# is_referral = fields.Boolean(string="Is Referral")
	referral_earning = fields.Float(string="Referral Earning",compute='_compute_points_count',readonly="1")
	parent_user_id = fields.Many2one('res.users', string='parent Referral User',readonly="1")
	# is_direct is told about the referral partner is craeted by mail or direct referral code
	is_direct = fields.Boolean(string="Is Direct",readonly="1")

	@api.one
	def _compute_points_count(self):
		for o in self:
			cdt = 0
			dbt = 0
			if o.referral_code:
				transaction = o.env['transaction.history'].search([('state','=','approve'),('referral_code','=',o.referral_code)])
				for t in transaction:
					_logger.info("--------transaction--%r------",t)
					if t.point_type == 'c':
						cdt += t.total_amount
					else:
						dbt += t.total_amount
			o.referral_earning = cdt - dbt


	def generate_referralCode(self):
		ran_ref = ''.join(random.choice('0123456789ABCDEFGHIJ0123456789KLMNOPQRSTUVWXYZ') for i in range(10))
		return ran_ref


	def _createReferralAccount(self, partner_id,parent_referral_code,user_id):
		PartnerObj= self.sudo().search([('id','=',partner_id)])
		TransactionObj = self.env['transaction.history'].sudo()
		parentReferralExist = self.validateParentReferral(parent_referral_code)
		if parentReferralExist['success']:
			PartnerObj.write({
				'referral_code':self.generate_referralCode(),
				'parent_user_id':parentReferralExist['user_id']
				})
			return {
					'is_parent_referral': True,
					'parent_user_id'   : parentReferralExist['user_id']
			}
		else:
			PartnerObj.write({
				'referral_code':self.generate_referralCode(),
				})
			return {
				'is_parent_referral':False
			}


# validate parent referral code and Add commission
	def validateParentReferral(self,parent_referral_code):
		UserObj= self.env['res.users'].sudo().search([('referral_code','=',parent_referral_code)])
		if len(UserObj) == 1:
			return {
				'success'  :  True,
				'result'   : 'Parent referral code exist',
				'user_id'   : UserObj.id,
			}
		else:
			return{
				'success'  : False,
				'result'   : 'Parent referral code not exist'

			}

	@api.one
	def getSignedUpReferralCount(self):
		return int(self.search_count([('parent_user_id','=',int(self.user_ids[0]))]))

	@api.one
	def getReferralAmount(self):
		return int(self.referral_earning)

	@api.one
	def getDirectSignedUpReferralCount(self):
		return int(self.search_count([('parent_user_id','=',int(self.user_ids[0])),('is_direct','=',True)]))


	def compute_mail_context(self,text):
		self.ensure_one()
		text = text.replace("{{reward_amt}}", self.textReplace("reward_amt"))
		text = text.replace("{{website_name}}", self.textReplace("website_name"))
		text = text.replace("{{referral_code}}", self.textReplace("referral_code"))
		text = text.replace("{{signup_link}}", self.textReplace("signup_link"))
		text = text.replace("{{user_name}}", self.textReplace("user_name"))
		text = text.replace(",", '%2C')
		# http://www.zaposphere.com/html-email-links-code/
		return text

	def textReplace(self,key):
		signup_link = self.env['ir.config_parameter'].sudo().get_param('web.base.url')+"/web/signup?referral="+self.referral_code
		website_name = self.env['website'].search([])[0].name
		referral_points = self.env['ir.default'].get('res.config.settings', 'referral_points')
		equivalent_amount = self.env['ir.default'].get('res.config.settings', 'equivalent_amount')
		val = {
		'reward_amt':self.currency_id.symbol+str(referral_points*equivalent_amount),
		'website_name':website_name,
		'referral_code':self.referral_code,
		'signup_link':signup_link,
		'user_name':self.name,
		}
		return val.get(key)
