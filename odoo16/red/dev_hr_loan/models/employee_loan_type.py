# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class employee_loan_type(models.Model):
	_name = 'employee.loan.type'
	_description = 'Type of employee Loan'
	

	def _compute_loan_done(self):
		for record in self:
			emp_loan = self.env['employee.loan'].search([('state','=','done'),('loan_type_id','=',record.id)])
			record.count_loan_done = len(emp_loan)
			
	def _compute_loan_paid(self):
		for record in self:
			emp_loan = self.env['employee.loan'].search([('state','=','paid'),('loan_type_id','=',record.id)])
			record.count_loan_paid = len(emp_loan)
			
	def _compute_loan_draft(self):
		for record in self:
			emp_loan = self.env['employee.loan'].search([('state','=','draft'),('loan_type_id','=',record.id)])
			record.count_loan_draft = len(emp_loan)

	def _get_default_currency(self):
		return self.env.user.company_id.currency_id


	name = fields.Char('Name', required="1")
	# loan_limit = fields.Float('Employee Loan Amount Limit', required="1")
	loan_term = fields.Integer('Employee Loan Term', default=6, required="1")
	loan_term.ondelete = None
	is_apply_interest = fields.Boolean('Apply Interest')
	interest_rate = fields.Float('Interest Rate (%) P.M',default=6)
	interest_type = fields.Selection([('liner','Linear'),('reduce','Reduce')],string='Interest Type', default='liner')
	loan_account = fields.Many2one('account.account',string='Loan Account')
	interest_account = fields.Many2one('account.account',string='Interest Account')
	journal_id = fields.Many2one('account.journal',string='Journal')
	color = fields.Integer(string= 'Color')
	count_loan_draft = fields.Integer(compute='_compute_loan_draft')
	count_loan_done = fields.Integer(compute='_compute_loan_done')
	count_loan_paid = fields.Integer(compute='_compute_loan_paid')
	priority = fields.Selection([('0','Low'),('1','Normal')],default='0')
	allow_loan_on_probation = fields.Boolean('Allow Loan on Probation')
	allow_multiple_loans = fields.Boolean(string='Allow Multiple Loans')
	
	is_apply_service_charge = fields.Boolean('Apply Service Charge')
	service_charge = fields.Float('Service Charge (%)', default=0.0)
	company_id = fields.Many2one('res.company', string='Company', required=True)
	company_loan_limit = fields.Float('Company Loan Limit', required=True)
	company_loan_term = fields.Integer('Company Loan Term', default=12, required=True)
	currency_id = fields.Many2one('res.currency', string='Currency', default=_get_default_currency)
	employee_id = fields.Many2one('hr.employee', string='Employee')
	multiplier = fields.Integer('Salary multiplier', default=0)
	terms_and_conditions = fields.Html(string='Terms and Conditions')
	terms_and_conditions_input = fields.Text(string='Enter Terms and Conditions')

	def save_terms_and_conditions(self):
		if self.terms_and_conditions_input:
			if not self.terms_and_conditions:
				self.terms_and_conditions = self.terms_and_conditions_input
			else:
				# Append the new terms and conditions to the existing ones
				self.terms_and_conditions += "<p>" + self.terms_and_conditions_input + "</p>" 

		# Clear the input field after saving the terms and conditions
		self.terms_and_conditions_input = ''

	# @api.model
	# def clear_last_term(self):
	#     if self.terms_and_conditions:
	#         # Split the terms and conditions into separate lines
	#         lines = self.terms_and_conditions.split("\n")
	#         # Remove the last line (last term)
	#         if len(lines) > 1:
	#             lines.pop()
	#         # Join the lines back together
	#         self.terms_and_conditions = "\n".join(lines)
	
	def _get_action(self, action_xmlid):
		# TDE TODO check to have one view + custo in methods
		action = self.env.ref(action_xmlid).read()[0]
		if self:
			action['display_name'] = self.display_name
		return action

	def get_action_loan_tree_done(self):
		return self._get_action('dev_hr_loan.action_loan_tree_done')
	
	def get_action_loan_tree_draft(self):
		return self._get_action('dev_hr_loan.action_loan_tree_draft')
	
	def action_get_hr_loan_type(self):
		return self._get_action('dev_hr_loan.get_hr_loan_type')
	def get_action_loan_paid(self):
		return self._get_action('dev_hr_loan.action_loan_paid')
	def get_action_hr_approval(self):
		return self._get_action('dev_hr_loan.action_hr_approval')
	
	def get_loan_create(self):
		return self._get_action('dev_hr_loan.action_loan_create')
	def get_all_loan(self):
		return self._get_action('dev_hr_loan.action_view_all_loan')
	def get_setting(self):
		return self._get_action('dev_hr_loan.action_setting')


	@api.constrains('is_apply_interest','interest_rate','interest_type')
	def _check_interest_rate(self):
		for loan in self:
			if loan.is_apply_interest:
				if loan.interest_rate <= 0:
					raise ValidationError("Interest Rate must be greater 0.00")
				if not loan.interest_type:
					raise ValidationError("Please Select Interest Type")

	@api.constrains('allow_loan_on_probation')
	def _check_loan_constraints(self):
		if self.allow_loan_on_probation:
			raise ValidationError('Cannot allow loan on probation')

	@api.constrains('is_apply_service_charge', 'service_charge')
	def _check_service_charge(self):
		for loan in self:
			if loan.is_apply_service_charge and loan.service_charge < 0:
				raise ValidationError("Service Charge cannot be negative")

	def _compute_service_charge(self):
		for loan in self:
			if loan.allow_service_charge:
				loan.service_charge = loan.loan_amount * loan.service_charge / 100

	@api.constrains('loan_term')
	def _check_loan_term(self):
		for record in self:
			max_loan_term = record.loan_term
			company_loan_term = record.company_loan_term
			if max_loan_term < 1:
				raise ValidationError("Loan term must be greater than or equal to 1.")
			elif max_loan_term > company_loan_term:
				raise ValidationError("Loan term cannot exceed the company loan term.")

	@api.constrains('company_loan_term')
	def _check_company_loan_term(self):
		for record in self:
			company_loan_term = record.company_loan_term
			if company_loan_term < 1:
				raise ValidationError("Company loan term must be greater than or equal to 1.")
			elif company_loan_term > 100:
				raise ValidationError("Company loan term cannot exceed 100 months.")

	# @api.constrains('loan_limit')
	# def _check_loan_limit(self):
	#     for record in self:
	#         loan_limit = record.loan_limit
	#         company_loan_limit = record.company_loan_limit
	#
	#         if loan_limit > company_loan_limit:
	#             raise ValidationError("Employee loan amount limit cannot exceed the company loan limit.")

	# def create_loan(self):
	#     if not self.allow_multiple_loans:
	#         existing_loan = self.env['loan.model'].search(
	#             [('employee_id', '=', self.employee_id.id), ('state', '=', 'done')])
	#         if existing_loan:
	#             raise ValueError('A loan already exists for this employee.')




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
