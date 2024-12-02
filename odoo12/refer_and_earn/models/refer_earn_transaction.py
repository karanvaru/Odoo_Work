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
class ReferEarnTransaction(models.Model):

	_name = 'transaction.history'
	_order = 'id desc'

	name = fields.Char(string="Name")
	user_id = fields.Many2one('res.users', string='User', readonly=True,help="User detail from which Transaction belong")
	partner_id = fields.Many2one('res.partner', compute='_get_partner_id',help="Customer detail from which Transaction belong")
	points = fields.Float(string="Points",readonly=True)
	reason = fields.Char(String="Reason")
	state = fields.Selection([
		("draft","Pending"),
		("reject","Rejected"),
		("cancel","Cancel"),
		("error","Error"),
		("approve","Approved"),
		], string="State",required=True,default="draft")
	point_type = fields.Selection([
		("c","Credit"),
		("d","Debit"),
		],string="Transaction Type")
	commission_type = fields.Selection([
		("parent","Referrer"),
		("child","Referral"),
		],string="Bonus Type")

	# Referrer, who invited another participant by using some link/code/ PARENT
	# Referral is a person who was invited by Referrer. / CHILD
	parent_id = fields.Many2one('res.users',string = 'Referrer')
	child_id = fields.Many2one('res.users',string = 'Referral')
	referral_code = fields.Char(string = "Referral Code",related='user_id.referral_code')
	total_amount = fields.Float(String="Total Amount")
	currency_id = fields.Many2one('res.currency', string='Currency', required=True,
	 readonly=True,default=lambda self: self.env.user.company_id.currency_id.id)
	debit_sale_order_id = fields.Many2one('sale.order', string='Debit Sale Order')
	first_sale_order_id = fields.Many2one('sale.order', string='First Sale Order')


	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('transaction.history')
		new =  super(ReferEarnTransaction,self).create(vals)
		return new

	@api.multi
	@api.depends('user_id')
	def _get_partner_id(self):
		for o in self:
			o.partner_id = o.user_id.partner_id.id


	@api.model
	def get_commission_pts(self,point_type):
		# point_type is either 'referral_points' or 'refered_points' or 'equivalent_amount'
		return self.env['res.config.settings'].get_values()[point_type]

	@api.model
	def get_default_commission_settings(self):
		# point_type is either 'auto_approve_request' or afterOrder
		return self.env['res.config.settings'].get_values()

	@api.multi
	def action_approve(self):
		self.write({'state': 'approve'})

	@api.multi
	def action_reject(self):
		self.write({'state': 'reject'})

	@api.multi
	def action_cancel(self):
		self.write({'state': 'cancel'})




	def _createTransactionSignup(self,partner_id,user_id,parent_user_id):
		self.setChildSignupCommission(user_id = user_id , parent_id = parent_user_id)
		self.setParentSignupCommission(user_id = parent_user_id , child_id = user_id)


	def setChildSignupCommission(self,user_id,parent_id):
		"""set refferal commission or child commission"""
		ParentDetail = self.env['res.users'].browse([parent_id])
		self.create({
			'user_id'           :user_id,
			'points'            :self.get_commission_pts('referral_points'),
			'reason'            :"Referrer Bonus for "+ParentDetail.name,
			'commission_type'   :'child',
			'parent_id'         :parent_id,
			'state'             :'approve',
			# (child or refferal) get on the spot commission so the state is approve
			'point_type'        :'c',
			'total_amount'      :self.get_commission_pts('referral_points')*self.get_commission_pts('equivalent_amount'),
			})

	def setParentSignupCommission(self,user_id,child_id):
		"""set Referrer commission or parent commission"""
		self.create({
			'user_id'           :user_id,
			'points'            :self.get_commission_pts('refered_points'),
			'reason'            :"Referral Bonus ",
			'state'             :self.set_state(),# parent
			'commission_type'   :'parent',
			'child_id'          :child_id,
			'point_type'        :'c',
			'total_amount'      :self.get_commission_pts('refered_points')*self.get_commission_pts('equivalent_amount'),
			})

	def _createInvalidTransactionSignup(self,user_id,invalid_referal):
		self.create({
			'user_id'           :user_id,
			'points'            :self.get_commission_pts('referral_points'),
			'reason'            :"No user found for Referral code ("+invalid_referal+")",
			# cancel state is non bidirectional
			'state'             :'cancel',
			'commission_type'   :'child',
			'point_type'        :'c',
			'total_amount'      :self.get_commission_pts('referral_points')*self.get_commission_pts('equivalent_amount'),
			})


	def _create_ReferaldebitTransaction(self,user_id,amount,order_id,order_name):
		self.create({
			'user_id'            :user_id,
			'points'             :amount/self.get_commission_pts('equivalent_amount'),
			'reason'             :"You used earned points "+ order_name,
			'state'              :'approve',
			'point_type'         :'d',
			'total_amount'       :amount,
			'debit_sale_order_id':order_id,
			})




	def addComsnOnFirstSale(self , user_id,first_order):
		"""this methods is used when the sale order is directly at state 'sale'
		means payments methods is used via payment gateway or wallet amount is greater then the sale value amount"""
		userDetail = self.env['res.users'].sudo().browse(user_id)
		transaction_child = self.search([('user_id','=',userDetail.id),('parent_id','=',userDetail.partner_id.parent_user_id.id),('commission_type','=','child')])
		if len(transaction_child) == 1 and transaction_child.state == 'approve':
			transaction_child.first_sale_order_id = first_order

		transaction_parent = self.search([('user_id','=',userDetail.partner_id.parent_user_id.id),('child_id','=',userDetail.id),('commission_type','=','parent')])
		if len(transaction_parent) == 1 and (transaction_parent.state == 'draft' or transaction_parent.state == 'approve'):
			transaction_parent.state = 'approve'
			transaction_parent.first_sale_order_id = first_order

	def addFirstOrderTransaction(self,user_id,first_order):
		"""this methods is used when the sale order is not at state 'sale'
		means payments methods is used via wire transfer etc"""
		userDetail = self.env['res.users'].sudo().browse(user_id)
		transaction_child = self.search([('user_id','=',userDetail.id),('parent_id','=',userDetail.partner_id.parent_user_id.id),('commission_type','=','child')])
		if transaction_child and len(transaction_child) == 1 :
			if transaction_child.state == 'approve':
				transaction_child.first_sale_order_id = first_order

		transaction_parent = self.search([('user_id','=', userDetail.partner_id.parent_user_id.id),('child_id','=',userDetail.id),('commission_type','=','parent')])
		if transaction_parent and len(transaction_parent) == 1 :
			if transaction_parent.state == 'draft':
				transaction_parent.first_sale_order_id = first_order



	def set_state(self):
		"""this set_state() method is used for set the state of transacton of parent or Referrer"""
		comsnOn = self.get_default_commission_settings()
		if comsnOn['verify_commission'] == 'autoApprove':
			return 'approve'
		else:
			if comsnOn['verify_commission'] == 'afterOrder':
				return 'draft'
			else:
				return 'error'

	def pretty_date(self):
		self.ensure_one()
		return fields.Datetime.from_string(self.create_date).strftime("%A %d %B %Y")

	def style(self):
		self.ensure_one()
		color = ""
		if self.state   == 'draft':
			color = "#ec971f"
		elif self.state == 'reject':
			color = "red"
		elif self.state == 'cancel':
			color = "#b733ad"
		elif self.state == 'error':
			color = "#3c763d"
		elif self.state == 'approve':
			color = "#337ab7"
		return color

	def _printstate(self):
		self.ensure_one()
		state = ""
		if self.state   == 'draft':
			state = "Pending"
		elif self.state == 'reject':
			state = "Rejected"
		elif self.state == 'cancel':
			state = "Cancelled"
		elif self.state == 'error':
			state = "Error"
		elif self.state == 'approve':
			state = "Approved"
		return state
