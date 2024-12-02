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
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta


import logging

_logger = logging.getLogger(__name__)


class employee_loan(models.Model):
	_name = 'employee.loan'
	_description = 'Loan of an Employee'
	_inherit = 'mail.thread'
	_order = 'name desc'

	loan_state = [('draft', 'Draft'),
				  ('request', 'Submit Request'),
				  ('ca_approval', 'Country Accountant Approval'),
				  ('dep_approval', 'Manager Approval'),
				  ('hr_approval', 'HR Approval'),
				  ('cfo_approval', 'CFO Approval'),
				  ('super_approval', 'CLHRO Approval'),
				  ('paid', 'Paid'),
				  ('done', 'Active'),
				  ('close', 'Close'),
				  ('reject', 'Rejected'),
				  ('cancel', 'Cancel')]

	@api.model
	def _get_employee(self):
		employee_id = self.env['hr.employee'].sudo().search(
			[('user_id', '=', self.env.user.id)], limit=1)
		return employee_id

	@api.model
	def _get_active_contract(self):
		employee = self._get_employee()
		if employee:
			contract = self.env['hr.contract'].sudo().search(
				[('employee_id', '=', employee.id), ('state', '=', 'open')],
				limit=1)
			return contract.id
		return False

	@api.model
	def _get_default_user(self):
		return self.env.user

	def send_loan_detail(self):
		if self.employee_id and self.employee_id.work_email:
			template_id = self.env['ir.model.data']._xmlid_lookup(
				'dev_hr_loan.dev_employee_loan_detail_send_mail')[2]
			template_id = self.env['mail.template'].browse(template_id)
			template_id.send_mail(self.ids[0], True)
		return True

	@api.depends('start_date', 'loan_term')
	def _get_end_date(self):
		for loan in self:
			end_date = False
			if loan.start_date and loan.loan_term:
				start_date = loan.start_date
				end_date = start_date + relativedelta(months=loan.loan_term)
			loan.end_date = end_date

	@api.onchange('date')
	def _onchange_date(self):
		for record in self:
			if record.date:
				last_day_of_month = record.date + relativedelta(day=31)
				record.start_date = last_day_of_month.strftime('%Y-%m-%d')

	@api.depends('installment_lines', 'paid_amount')
	def get_extra_interest(self):
		for loan in self:
			amount = 0
			for installment in loan.installment_lines:
				if installment.is_skip:
					amount += installment.ins_interest
			loan.extra_in_amount = amount

	name = fields.Char('Name', default='/', copy=False)
	state = fields.Selection(loan_state, string='State', default='draft',
							 track_visibility='onchange')
	employee_id = fields.Many2one('hr.employee',
								  default=lambda self: self._get_employee(),
								  required="1")
	department_id = fields.Many2one('hr.department', string='Department',
									related='employee_id.department_id')
	hr_manager_id = fields.Many2one('hr.employee', string='Hr Manager')
	country_accountant_id = fields.Many2one('hr.employee',
											string='Country Accountant Manager')
	cfo_id = fields.Many2one('hr.employee', string='CFO Manager')
	super_approver_id = fields.Many2one('hr.employee', string='Super Approver')
	manager_id = fields.Many2one('hr.employee', string='Line Manager',
								 related='employee_id.parent_id', readonly=True)
	job_id = fields.Many2one('hr.job', string="Job Position",
							 related='employee_id.job_id')
	date = fields.Date('Date', default=fields.Date.today())
	start_date = fields.Date('Start Date', required="1")
	end_date = fields.Date('End Date', compute='_get_end_date')
	term = fields.Integer('Term', readonly=True)
	loan_term = fields.Integer('Loan Term', required="1")
	loan_type_id = fields.Many2one('employee.loan.type', string='Loan Type',
								   required="1")
	payment_method = fields.Selection([('by_payslip', 'By Payslip')],
									  string='Payment Method',
									  default='by_payslip', required="1")
	loan_amount = fields.Float('Loan Amount', required="1")
	paid_amount = fields.Float('Paid Amount', compute='get_paid_amount')
	remaining_amount = fields.Float('Remaining Amount',
									compute='get_remaining_amount')
	installment_amount = fields.Float('Installment Amount', required="1",
									  compute='get_installment_amount')
	loan_url = fields.Char('URL', compute='get_loan_url')
	user_id = fields.Many2one('res.users', default=_get_default_user)
	is_apply_interest = fields.Boolean('Apply Interest')
	interest_type = fields.Selection(
		[('liner', 'Linear'), ('reduce', 'Reduce')], string='Interest Type')
	interest_rate = fields.Float(string='Interest Rate (%)')
	is_apply_service_charge = fields.Boolean('Apply Service Charge')
	service_charge = fields.Float(string='Service Charge (%)')
	interest_amount = fields.Float('Interest Amount',
								   compute='get_interest_amount', store=True)
	installment_lines = fields.One2many('installment.line', 'loan_id',
										string='Installments', )
	service_charge_amount = fields.Float('Service Charge Amount',
										 compute='get_service_charge_amount')
	notes = fields.Text('Reason', required="1")
	is_close = fields.Boolean('IS close', compute='is_ready_to_close')
	move_id = fields.Many2one('account.move', string='Journal Entry')
	loan_document_line_ids = fields.One2many('dev.loan.document', 'loan_id',
											 required="1")
	installment_count = fields.Integer(compute='get_interest_count')
	company_id = fields.Many2one('res.company', string='Company',
								 related='employee_id.company_id', store=True,
								 readonly=True,
								 default=lambda self: self.env.company)
	allow_multiple_loans = fields.Boolean('Allow Multiple Loans',
										  related='loan_type_id.allow_multiple_loans',
										  store=True)
	currency_id = fields.Many2one('res.currency', string='Currency',
								  related='loan_type_id.currency_id',
								  readonly=True, store=True)
	ca_approval_reason = fields.Text('Country Accountant Approval Reason')
	dep_manager_approval_reason = fields.Text(
		'Department Manager Approval Reason')
	hr_approval_reason = fields.Text('HR Manager Approval Reason')
	cfo_approval_reason = fields.Text('CFO Approval Reason')
	super_approver_approval_reason = fields.Text('CEO Approval Reason')
	ca_reject_reason = fields.Text('Country Accountant Rejection Reason')
	dep_manager_reject_reason = fields.Text(
		'Department Manager Rejection Reason')
	hr_reject_reason = fields.Text('HR Manager Rejection Reason')
	cfo_reject_reason = fields.Text('CFO Rejection Reason')
	super_approver_reject_reason = fields.Text('CEO Rejection Reason')
	contract_id = fields.Many2one('hr.contract', 'Contract', default=lambda
		self: self._get_active_contract())
	n_paid_amount = fields.Float(related='paid_amount', string='Paid Amount',
								 store=True)
	wage = fields.Float(string='Wage', compute='_compute_wage', store=True)
	multiplied_wage = fields.Float(string='Maximum Loan Qualified',
								   compute='_compute_multiplied_wage',
								   store=True)
	multiplier = fields.Integer('Salary multiplier',
								related='loan_type_id.multiplier', store=True)
	terms_and_conditions = fields.Text(string='Terms and Conditions')
	accepted_terms = fields.Boolean(string='Terms and Conditions',
									default=False)

	extra_in_amount = fields.Float('Extra Int. Amount',
								   compute='get_extra_interest')
	n_extra_in_amount = fields.Float(related='extra_in_amount',
									 string='Extra Interest Amount', store=True)
	n_interest_amount = fields.Float(related='interest_amount',
									 string='Interest Amount', store=True)
	n_remaining_amount = fields.Float(related='remaining_amount',
									  string='Remaining Amount', store=True)

	is_current_manager = fields.Boolean(
		string="Is Current Manager",
		compute='_compute_is_current_manager',
		readonly=True,
		store=False
	)

	@api.depends('manager_id')
	def _compute_is_current_manager(self):
		current_user = self.env.user
		for loan in self:
			loan.is_current_manager = loan.manager_id == current_user.employee_id

	@api.onchange('loan_type_id')
	def _onchange_loan_type(self):
		if self.loan_type_id:
			self.term = self.loan_type_id.loan_term

	@api.constrains('accepted_terms')
	def _check_accepted_terms(self):
		for record in self:
			if not record.accepted_terms:
				raise ValidationError("You must accept the terms before saving the form.")

	@api.constrains('loan_document_line_ids')
	def _check_loan_document(self):
		for record in self:
			if not record.loan_document_line_ids:
				raise ValidationError(
					"You must upload a document before saving the form.")

	@api.model
	def create(self, vals):
		if 'loan_type_id' in vals:
			loan_type = self.env['loan.type'].browse(vals['loan_type_id'])
			if loan_type:
				vals['term'] = loan_type.loan_term
		return super(employee_loan, self).create(vals)

	def write(self, vals):
		if 'loan_type_id' in vals:
			loan_type = self.env['loan.type'].browse(vals['loan_type_id'])
			if loan_type:
				vals['term'] = loan_type.loan_term
		return super(employee_loan, self).write(vals)

	@api.model
	def _default_company_id(self):
		employee = self.env['hr.employee'].sudo().search(
			[('user_id', '=', self.env.user.id)], limit=1)
		if employee:
			return employee.company_id.id
		else:
			default_company = self.env['res.company'].sudo().search([], limit=1)
			return default_company.id if default_company else False

	@api.depends('employee_id')
	def _compute_wage(self):
		for loan in self:
			loan.wage = loan.employee_id.contract_id.wage

	@api.depends('wage', 'multiplier')
	def _compute_multiplied_wage(self):
		for loan in self:
			loan.multiplied_wage = loan.wage * loan.multiplier

	@api.onchange('loan_type_id')
	def _on_loan_type_change(self):
		if self.loan_type_id:
			self.terms_and_conditions = self.loan_type_id.terms_and_conditions

	@api.constrains('contract_id')
	def _check_employee_contract(self):
		if not self.contract_id:
			raise ValidationError(
				_("You currently do not have a contract associated to you. \n Contact HR."))

	@api.constrains('loan_term')
	def _check_loan_term(self):
		if not self.loan_term or self.loan_term <= 0:
			raise ValidationError('Loan Term must be greater than zero.')

	@api.model
	def create(self, vals):
		loan = super(employee_loan, self).create(vals)
		if loan.loan_type_id:
			loan.terms_and_conditions = loan.loan_type_id.terms_and_conditions
		return loan

	def write(self, vals):
		if 'loan_type_id' in vals:
			loan_type_id = self.env['employee.loan.type'].browse(
				vals['loan_type_id'])
			vals['terms_and_conditions'] = loan_type_id.terms_and_conditions
		return super(employee_loan, self).write(vals)

	@api.depends('installment_lines')
	def get_interest_count(self):
		for loan in self:
			count = 0
			if loan.installment_lines:
				count = len(loan.installment_lines)
			loan.installment_count = count

	@api.onchange('term', 'interest_rate', 'interest_type', 'service_charge')
	def onchange_term_interest_type(self):
		if self.loan_type_id:
			self.term = self.loan_type_id.loan_term
			self.interest_rate = self.loan_type_id.interest_rate
			self.interest_type = self.loan_type_id.interest_type
			self.service_charge = self.loan_type_id.service_charge

	@api.depends('remaining_amount')
	def is_ready_to_close(self):
		for loan in self:
			ready = False
			if loan.remaining_amount <= 0 and loan.state == 'done':
				ready = True
			loan.is_close = ready

	@api.depends('installment_lines')
	def get_paid_amount(self):
		for loan in self:
			amt = 0
			for line in loan.installment_lines:
				if line.is_paid:
					if line.is_skip:
						amt += line.ins_interest
					else:
						amt += line.total_installment
			loan.paid_amount = amt

	def compute_installment(self):
		self.ensure_one()  # Ensure the method is called on a single record
		vals = []
		amount = self.loan_amount / self.loan_term
		total_installment_amount = 0.0

		for i in range(0, self.loan_term):
			date = self.start_date + relativedelta(months=i)
			service_charge_amount = self.service_charge_amount / self.loan_term
			interest_amount = 0.0
			ins_interest_amount = 0.0

			if self.is_apply_interest:
				if self.interest_type == 'liner':
					interest_amount =self.interest_amount / self.loan_term
					# interest_amount = (self.loan_amount * (
					# 		self.interest_rate / 100)) * self.loan_term
				elif self.interest_type == 'reduce':
					interest_amount = (amount * self.interest_rate) / (12 * 100)
				ins_interest_amount = interest_amount / self.loan_term

			installment_amount = amount + service_charge_amount + ins_interest_amount
			total_installment_amount += installment_amount

			vals.append((0, 0, {
				'name': 'INS - ' + self.name + ' - ' + str(i + 1),
				'employee_id': self.employee_id.id if self.employee_id else False,
				'date': date,
				'amount': amount,
				'interest': interest_amount,
				'service_charge_amount': service_charge_amount,
				'installment_amt': installment_amount,
				'ins_interest': ins_interest_amount,
			}))

			# Ensure each installment amount does not exceed the employee's wage
			# if self.employee_id and self.employee_id.contract_id:
			# 	contract_wage = self.employee_id.contract_id.wage
			# 	if self.end_date:
			# 		# Convert date_start and date_end to datetime objects
			# 		date_start_datetime = datetime.combine(self.start_date,
			# 											   datetime.min.time())
			# 		date_end_datetime = datetime.combine(self.end_date,
			# 											 datetime.min.time())
			# 		# Fetch relevant deductions (permanent and date range overlaps)
			# 		deductions = self.env['ke.deductions'].search([
			# 			('employee_id', '=', self.employee_id.id),
			# 			'|',
			# 			'&', ('date_start', '<=', date_end_datetime),
			# 			('date_end', '>=', date_start_datetime),
			# 			'&', ('date_start', '<=', date_end_datetime),
			# 			('is_permanent', '=', True)
			# 		])
			# 		total_deductions = sum(deduction.amount for deduction in deductions)
			# 		# Fetch relevant allowances (permanent and date range overlaps)
			# 		allowances = self.env['ke.cash_allowances'].search([
			# 			('contract_id', '=', self.contract_id.id),
			# 			'|',
			# 			'&', ('date_start', '<=', date_end_datetime),
			# 			('date_end', '>=', date_start_datetime),
			# 			'&', ('date_start', '<=', date_end_datetime),
			# 			('is_permanent', '=', True)
			# 		])
			# 		total_allowances = sum(allowance.amount for allowance in allowances)
			# 		if total_deductions + installment_amount > contract_wage + total_allowances:
			# 			raise ValidationError(
			# 				f"You cannot create a loan request. Your total deductions for the month are {total_deductions + installment_amount} which exceeds your gross wage {contract_wage + total_allowances}.")

		if self.installment_lines:
			self.installment_lines.unlink()
		self.installment_lines = vals
		return vals

	@api.depends('paid_amount', 'loan_amount', 'interest_amount',
				 'service_charge_amount')
	def get_remaining_amount(self):
		for loan in self:
			remaining = (
									loan.loan_amount + loan.interest_amount + loan.service_charge_amount) - loan.paid_amount
			loan.remaining_amount = remaining

	@api.onchange('loan_amount', 'loan_term', 'interest_rate', 'interest_type',
				  'is_apply_interest',
				  'installment_lines')
	def _onchange_compute_interest(self):
		if self.is_apply_interest and self.interest_type and self.interest_rate:
			self.get_interest_amount()

	@api.depends('loan_amount', 'interest_rate', 'interest_type',
				 'is_apply_interest', 'installment_lines')
	def get_interest_amount(self):
		for loan in self:
			loan.interest_amount = 0.0

			if loan.is_apply_interest:
				if loan.interest_type == 'liner':
					loan.interest_amount += (loan.loan_amount * (
								loan.interest_rate / 100)) * loan.loan_term
				elif loan.interest_type == 'reduce':
					loan.interest_amount += (loan.loan_amount * (
								loan.interest_rate / 100)) * loan.loan_term

	@api.depends('loan_amount', 'service_charge')
	def get_service_charge_amount(self):
		for loan in self:
			if loan.service_charge:
				service_charge_amount = loan.loan_amount * (
							loan.service_charge / 100)
			else:
				service_charge_amount = 0
			loan.service_charge_amount = service_charge_amount

	@api.onchange('interest_type', 'interest_rate')
	def onchange_interest_rate_type(self):
		if self.interest_type and self.is_apply_interest:
			if self.interest_rate != self.loan_type_id.interest_rate:
				self.interest_rate = self.loan_type_id.interest_rate
			if self.interest_type != self.loan_type_id.interest_type:
				self.interest_type = self.loan_type_id.interest_type

	@api.onchange('is_apply_service_charge')
	def onchange_is_apply_service_charge(self):
		if not self.is_apply_service_charge:
			self.service_charge = 0.0

	def update_service_charge(self):
		if self.is_apply_service_charge and self.loan_type_id:
			self.service_charge = self.loan_type_id.service_charge

	@api.depends('employee_id', 'company_id')
	def get_loan_url(self):
		for loan in self:
			ir_param = self.env['ir.config_parameter'].sudo()
			base_url = ir_param.get_param('web.base.url')
			action_id = self.env.ref('dev_hr_loan.action_employee_loan').id
			menu_id = self.env.ref('dev_hr_loan.menu_employee_loan').id
			company_id = self.company_id.id
			if base_url:
				base_url += '/web#id=%s&action=%s&model=%s&view_type=form&cids=%s&menu_id=%s' % (
				loan.id, action_id, 'employee.loan', company_id, menu_id)
			loan.loan_url = base_url

	@api.depends('loan_term', 'loan_amount', 'interest_amount',
				 'service_charge_amount')
	def get_installment_amount(self):
		for loan in self:
			if loan.loan_amount and loan.loan_term:
				total_amount = loan.loan_amount + loan.interest_amount + loan.service_charge_amount
				amount = total_amount / loan.loan_term

				loan.installment_amount = amount
			else:
				loan.installment_amount = 0.0

	# READD THIS CODE
	@api.constrains('employee_id')
	def _check_loan(self):
		now = datetime.now()
		year = now.year
		s_date = str(year) + '-01-01'
		e_date = str(year) + '-12-01'

		disallowed_states = ['draft', 'request', 'ca_approval', 'dep_approval',
							 'hr_approval', 'cfo_approval', 'paid', 'done']

		loan_ids = self.search([
			('employee_id', '=', self.employee_id.id),
			('date', '<=', e_date),
			('date', '>=', s_date),
			('state', 'not in', disallowed_states)
		])
		loan_count = len(loan_ids)

		if not self.allow_multiple_loans and loan_count > self.employee_id.loan_request:
			raise ValidationError(
				"You have an existing active loan and can only have %s application at a time" % self.employee_id.loan_request)

	@api.onchange('loan_type_id')
	def _onchange_loan_type(self):
		if self.loan_type_id:
			self.term = self.loan_type_id.loan_term
			self.is_apply_interest = self.loan_type_id.is_apply_interest
			if self.is_apply_interest:
				self.interest_rate = self.loan_type_id.interest_rate

	def get_country_accountant_email(self):
		group_id = self.env['ir.model.data']._xmlid_lookup(
			'dev_hr_loan.group_country_accountant')[2]
		group_ids = self.env['res.groups'].browse(group_id)
		email = ''
		if not self.country_accountant_id:
			if group_ids:
				employee_id = self.env['hr.employee'].sudo().search(
					[('user_id', 'in', group_ids.users.ids),
					('company_id', '=', self.company_id.id)], limit=1)

				if email:
					email = email + ',' + employee_id.work_email
				else:
					email = employee_id.work_email
				self.country_accountant_id = employee_id.id
		else:
			email = self.country_accountant_id.work_email
		return email

	def action_send_request(self):
		if not self.installment_lines:
			self.compute_installment()
		email = self.get_country_accountant_email()
		if email:
			ir_model_data = self.env['ir.model.data']
			template_id = ir_model_data._xmlid_lookup(
				'dev_hr_loan.dev_country_accountant_request')[2]
			mtp = self.env['mail.template']
			template_id = mtp.browse(template_id)
			template_id.write({'email_to': email})
			template_id.send_mail(self.ids[0], True)
		else:
			raise ValidationError(_("Country Accountant for Country not found"))
		self.state = 'ca_approval'

	def get_department_manager_email(self):
		group_id = self.env['ir.model.data']._xmlid_lookup(
			'dev_hr_loan.group_department_manager')[2]
		group_ids = self.env['res.groups'].browse(group_id)

		if group_ids:
			manager = self.manager_id
			employee = self.env['hr.employee'].sudo().search([
				('id', '=', manager.id)
			])
			email = employee.work_email
		return email

	def country_accountant_approval_loan(self):
		email = self.get_department_manager_email()
		if email:
			ir_model_data = self.env['ir.model.data']
			template_id = \
			ir_model_data._xmlid_lookup('dev_hr_loan.dev_dep_manager_request')[
				2]
			mtp = self.env['mail.template']
			template_id = mtp.browse(template_id)
			template_id.write({'email_to': email})
			template_id.send_mail(self.ids[0], True)
		else:
			raise ValidationError(
				_("Manager for Employee Not Found. Contact HR."))
		self.state = 'dep_approval'

	def get_hr_manager_email(self):
		group_id = \
		self.env['ir.model.data']._xmlid_lookup('dev_hr_loan.group_hr_manager')[
			2]
		group_ids = self.env['res.groups'].browse(group_id)
		if group_ids:
			employee_id = self.env['hr.employee'].sudo().search(
				[('user_id', 'in', group_ids.users.ids)], limit=1)
			email = employee_id.work_email
			self.hr_manager_id = employee_id.id
		return email

	def dep_manager_approval_loan(self):
		self.state = 'hr_approval'
		email = self.get_hr_manager_email()
		if email:
			ir_model_data = self.env['ir.model.data']
			template_id = \
			ir_model_data._xmlid_lookup('dev_hr_loan.dev_hr_manager_request')[2]
			mtp = self.env['mail.template']
			template_id = mtp.browse(template_id)
			template_id.write({'email_to': email})
			template_id.send_mail(self.ids[0], True)
		else:
			raise UserError(
				_("HR Manager Mail cannot be found. Kindly Contact HR"))

	def get_chief_financial_officer_email(self):
		group_id = \
		self.env['ir.model.data']._xmlid_lookup('dev_hr_loan.group_cfo')[2]
		group_ids = self.env['res.groups'].browse(group_id)
		if group_ids:
			employee_id = self.env['hr.employee'].sudo().search(
				[('user_id', 'in', group_ids.users.ids)], limit=1)
			email = employee_id.work_email
			self.cfo_id = employee_id.id
		return email

	def hr_manager_approval_loan(self):
		email = self.get_chief_financial_officer_email()
		if email:
			ir_model_data = self.env['ir.model.data']
			template_id = \
			ir_model_data._xmlid_lookup('dev_hr_loan.dev_cfo_request')[2]
			mtp = self.env['mail.template']
			template_id = mtp.browse(template_id)
			template_id.write({'email_to': email})
			template_id.send_mail(self.ids[0], True)
		else:
			raise UserError(_("CFO Email cannot be found. Kindly Contact HR"))
		self.state = 'cfo_approval'

	def get_super_approver_email(self):
		group_id = self.env['ir.model.data']._xmlid_lookup(
			'dev_hr_loan.group_super_approver')[2]
		group_ids = self.env['res.groups'].sudo().browse(group_id)
		roles = self.env['res.users.role'].sudo().search([
			('name', '=', 'CLHRO')
		], limit=1)
		email = ''
		if group_ids:
			employee_id = self.env['hr.employee'].sudo().search(
				[('user_id', 'in', group_ids.users.ids),
				 ('user_id', 'in', roles.users.ids)], limit=1)
			self.super_approver_id = employee_id.id
			email = employee_id.work_email
		return email

	def change_start_date(self):
		for rec in self:
			start_date = datetime.today().date()
			if rec.start_date.month <= start_date.month and int(start_date.day) > 20:
				# Calculate the new month by adding 1 month to today's month
				if rec.start_date.month == state_date.month:
					rec.start_date = start_date + relativedelta(months=1)
				else:
					month = start_date.month - rec.start_date.month
					rec.start_date = start_date + relativedelta(months=month+1)
				rec.compute_installment()
			
			



	def cfo_approval_loan(self):
		if self.loan_amount > self.multiplied_wage or self.loan_term > self.term:
			email = self.get_super_approver_email()
			if email:
				ir_model_data = self.env['ir.model.data']
				template_id = ir_model_data._xmlid_lookup(
					'dev_hr_loan.dev_super_approver_request')[2]
				mtp = self.env['mail.template']
				template_id = mtp.browse(template_id)
				template_id.write({'email_to': email})
				template_id.send_mail(self.ids[0], True)
			self.state = 'super_approval'
		else:
			employee_id = self.env['hr.employee'].sudo().search(
				[('user_id', '=', self.env.user.id)], limit=1)
			ir_model_data = self.env['ir.model.data']
			template_id = \
			ir_model_data._xmlid_lookup('dev_hr_loan.cfo_confirm_loan')[2]
			mtp = self.env['mail.template']
			template_id = mtp.browse(template_id)
			template_id.write({'email_to': self.employee_id.work_email})
			template_id.send_mail(self.ids[0], True)
			self.state = 'done'
			self.change_start_date()

	def super_approver_approval_loan(self):
		if self.employee_id.work_email and self.super_approver_id:
			ir_model_data = self.env['ir.model.data']
			template_id = ir_model_data._xmlid_lookup(
				'dev_hr_loan.super_approver_confirm_loan')[2]
			mtp = self.env['mail.template']
			template_id = mtp.browse(template_id)
			template_id.write({'email_to': self.employee_id.work_email})
			template_id.send_mail(self.ids[0], True)
		self.state = 'done'
		self.change_start_date()

	def country_accountant_reject_loan(self):
		self.state = 'reject'
		if self.employee_id.work_email:
			ir_model_data = self.env['ir.model.data']
			template_id = ir_model_data._xmlid_lookup(
				'dev_hr_loan.country_accountant_reject_loan')[2]
			mtp = self.env['mail.template']
			template_id = mtp.browse(template_id)
			template_id.write({'email_to': self.employee_id.work_email})
			template_id.send_mail(self.ids[0], True)

	def schedule_close_loan(self):
		records = self.env['employee.loan'].search([
			('remaining_amount', '<=', 0)
		])
		for rec in records:
			rec.action_close_loan()

	def action_close_loan(self):
		self.state = 'close'
		if self.employee_id.work_email and self.cfo_id:
			ir_model_data = self.env['ir.model.data']
			template_id = \
			ir_model_data._xmlid_lookup('dev_hr_loan.cfo_closed_loan')[2]
			mtp = self.env['mail.template']
			template_id = mtp.browse(template_id)
			template_id.write({'email_to': self.employee_id.work_email})
			template_id.send_mail(self.ids[0], True)

	def dep_manager_reject_loan(self):
		self.state = 'reject'
		if self.employee_id.work_email:
			ir_model_data = self.env['ir.model.data']
			template_id = \
			ir_model_data._xmlid_lookup('dev_hr_loan.dep_manager_reject_loan')[
				2]
			mtp = self.env['mail.template']
			template_id = mtp.browse(template_id)
			template_id.write({'email_to': self.employee_id.work_email})
			template_id.send_mail(self.ids[0], True)

	def hr_manager_reject_loan(self):
		self.state = 'reject'
		if self.employee_id.work_email:
			ir_model_data = self.env['ir.model.data']
			template_id = \
			ir_model_data._xmlid_lookup('dev_hr_loan.hr_manager_reject_loan')[2]
			mtp = self.env['mail.template']
			template_id = mtp.browse(template_id)
			template_id.write({'email_to': self.employee_id.work_email})
			template_id.send_mail(self.ids[0], True)

	def cfo_reject_loan(self):
		self.state = 'reject'
		if self.employee_id.work_email:
			ir_model_data = self.env['ir.model.data']
			template_id = \
			ir_model_data._xmlid_lookup('dev_hr_loan.cfo_reject_loan')[2]
			mtp = self.env['mail.template']
			template_id = mtp.browse(template_id)
			template_id.write({'email_to': self.employee_id.work_email})
			template_id.send_mail(self.ids[0], True)

	def super_approver_reject_loan(self):
		self.state = 'reject'
		if self.employee_id.work_email:
			ir_model_data = self.env['ir.model.data']
			template_id = ir_model_data._xmlid_lookup(
				'dev_hr_loan.super_approver_reject_loan')[2]
			mtp = self.env['mail.template']
			template_id = mtp.browse(template_id)
			template_id.write({'email_to': self.employee_id.work_email})
			template_id.send_mail(self.ids[0], True)

	def cancel_loan(self):
		self.state = 'cancel'

	def set_to_draft(self):
		self.state = 'draft'

	def paid_loan(self):
		if not self.employee_id.address_home_id:
			raise ValidationError(
				_('Employee Private Address is not selected in Employee Form !!!'))

		self.state = 'paid'
		vals = {
			'date': self.date,
			'ref': self.name,
			'journal_id': self.loan_type_id.journal_id and self.loan_type_id.journal_id.id,
			'company_id': self.env.user.company_id.id
		}
		acc_move_id = self.env['account.move'].create(vals)
		if acc_move_id:
			lst = []
			val = (0, 0, {
				'account_id': self.loan_type_id and self.loan_type_id.loan_account.id,
				'partner_id': self.employee_id.address_home_id and self.employee_id.address_home_id.id or False,
				'name': self.name,
				'credit': self.loan_amount or 0.0,
				'move_id': acc_move_id.id,
			})
			lst.append(val)

			if self.interest_amount:
				val = (0, 0, {
					'account_id': self.loan_type_id and self.loan_type_id.interest_account.id,
					'partner_id': self.employee_id.address_home_id and self.employee_id.address_home_id.id or False,
					'name': str(self.name) + ' - ' + 'Interest',
					'credit': self.interest_amount or 0.0,
					'move_id': acc_move_id.id,
				})
				lst.append(val)

			credit_account = False
			if self.employee_id.address_home_id and self.employee_id.address_home_id.property_account_payable_id:
				credit_account = self.employee_id.address_home_id.property_account_payable_id.id or False

			debit_amount = self.loan_amount
			if self.interest_amount:
				debit_amount += self.interest_amount
			val = (0, 0, {
				'account_id': credit_account or False,
				'partner_id': self.employee_id.address_home_id and self.employee_id.address_home_id.id or False,
				'name': '/',
				'debit': debit_amount or 0.0,
				'move_id': acc_move_id.id,
			})
			lst.append(val)
			acc_move_id.line_ids = lst
			self.move_id = acc_move_id.id

	def view_journal_entry(self):
		if self.move_id:
			return {
				'view_mode': 'form',
				'res_id': self.move_id.id,
				'res_model': 'account.move',
				'view_type': 'form',
				'type': 'ir.actions.act_window',
			}

	def action_done_loan(self):
		self.state = 'done'

	@api.model
	def create(self, vals):
		if vals.get('name', '/') == '/':
			vals['name'] = self.env['ir.sequence'].next_by_code(
				'employee.loan') or '/'
		return super(employee_loan, self).create(vals)

	def copy(self, default=None):
		if default is None:
			default = {}
		default['name'] = '/'
		return super(employee_loan, self).copy(default=default)

	def unlink(self):
		for loan in self:
			if loan.state != 'draft':
				raise ValidationError(_('Loan delete in draft state only !!!'))
		return super(employee_loan, self).unlink()

	def action_view_loan_installment(self):
		action = self.env.ref('dev_hr_loan.action_installment_line').read()[0]

		installment = self.mapped('installment_lines')
		if len(installment) > 1:
			action['domain'] = [('id', 'in', installment.ids)]
		elif installment:
			action['views'] = [
				(self.env.ref('dev_hr_loan.view_loan_emi_form').id, 'form')]
			action['res_id'] = installment.id
		return action
