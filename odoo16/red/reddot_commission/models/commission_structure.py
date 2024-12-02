# -*- coding: utf-8 -*-
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import base64

try:
	import simplejson as _json
except ImportError:
	import json as _json

import logging


_logger = logging.getLogger(__name__)



MONTH_SELECTION = [
	('1', 'January'),
	('2', 'February'),
	('3', 'March'),
	('4', 'April'),
	('5', 'May'),
	('6', 'June'),
	('7', 'July'),
	('8', 'August'),
	('9', 'September'),
	('10', 'October'),
	('11', 'November'),
	('12', 'December'),
]


class CommissionStructure(models.Model):
	_name = 'commission.structure'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = 'Commission Structure'

	@api.model
	def _get_year_options(self):
		years = []
		for i in range(2024, 2101):
			years.append((str(i), str(i)))
		return years

	name = fields.Char(
		string="Name",
		copy=False,
		readonly=True
	)

	user_id = fields.Many2one(
		'res.users',
		string="Sales Person",
		tracking=True,
		required=True
	)
	start_year = fields.Selection(
		selection="_get_year_options",
		default="2024",
		string="Start Year",
		required=True
	)
	end_year = fields.Selection(
		selection="_get_year_options",
		default="2024",
		string="End Year",
		required=True
	)
	start_month = fields.Selection(
		selection=MONTH_SELECTION,
		string="Start Month",
		required=True
	)
	end_month = fields.Selection(
		selection=MONTH_SELECTION,
		string="End Month",
		required=True
	)
	commission_type = fields.Selection(
		selection=[
			('self', 'Self'),
			('bu_wise', 'Bu Wise'),
			('bu_group_wise', 'Bu Group Wise'),
			('country_wise', 'Country Wise'),
			('company_wise', 'Company Wise'),
			('region_wise', 'Region Wise'),
		],
		required=True,
		string="Commission Type",
		tracking=True
	)
	commission_measure_type = fields.Selection(
		selection=[
			('revenue', 'Revenue'),
			('gross_profit', 'Gross Profit'),
			('both', 'Both')
		],
		string="Commission Measure Type",
		default="revenue",
		tracking=True
	)
	total_commission_amount = fields.Float(
		string="Commission Amount",
		copy=False
	)
	commission_structure_line_ids = fields.One2many(
		'commission.structure.line',
		'commission_structure_id',
		string="Lines",
		ondelete="cascade"
	)
	breadth_commission_structure_line_ids = fields.One2many(
		'commission.structure.line',
		'breadth_commission_structure_id',
		string="Breadth Lines",
		ondelete="cascade"
	)
	kpi_commission_structure_line_ids = fields.One2many(
		'commission.structure.kpi.line',
		'commission_structure_id',
		string="KPI Lines",
		ondelete="cascade"
	)
	ded_commission_structure_line_ids = fields.One2many(
		'commission.structure.deduction.line',
		'commission_structure_id',
		string="Deduction Lines",
		ondelete="cascade"
	)
	period_type = fields.Selection(
		selection=[
			('monthly', 'Monthly'),
			('quarterly', 'Quarterly'),
			('half_yearly', 'Half Yearly'),
			('yearly', 'Yearly'),
		],
		default="monthly",
		string="Period",
		required=True
	)
	start_date = fields.Date(
		string="Start Date",
	)
	end_date = fields.Date(
		string="End Date",
	)
	state = fields.Selection(
		selection=[
			('draft', 'Draft'),
			('sent', 'Sent'),
			('approved', 'Running'),
			('rejected', 'Rejected'),
			('validate', 'Closed'),
			('in_payment', 'In Payment'),
			('paid', 'Paid'),
		],
		string="Status",
		default='draft',
		tracking=True,
		copy=False
	)
	commission_currency_id = fields.Many2one(
		'res.currency',
		string='Currency',
	)
	apply_commission_revenue = fields.Boolean(
		string="Apply Revenue/GP Commission?",
		default=True
	)
	apply_commission_breadth = fields.Boolean(
		string="Apply Breadth Commission?",
		default=True
	)
	apply_commission_kpi = fields.Boolean(
		string="Apply KPI Commission?",
		default=True
	)
	revenue_gp_percentage = fields.Float(string="Revenue/GP Percentage")
	breadth_percentage = fields.Float(string="Breadth Percentage")
	kpi_percentage = fields.Float(string="KPI Percentage")

	apply_commission_deduction = fields.Boolean(
		string="Apply Deduction Commission?",
		default=True
	)
	deduction_percentage = fields.Float(string="Deduction Percentage")

	revenue_commission_amount = fields.Float(
		string="Revenue/GP Commission Amount",
		compute="_compute_all_amounts",
		store=True,
		copy=False
	)
	breadth_commission_amount = fields.Float(
		string="Breadth Commission Amount",
		compute="_compute_all_amounts",
		store=True,
		copy=False
	)
	kpi_commission_amount = fields.Float(
		string="KPI Commission Amount",
		compute="_compute_all_amounts",
		store=True,
		copy=False
	)
	deduction_commission_amount = fields.Float(
		string="Deduction Commission Amount",
		compute="_compute_all_amounts",
		store=True,
		copy=False
	)
	revenue_commission_achieved = fields.Float(
		string="Revenue/GP Commission Achived",
		compute="_compute_commission_achieved",
		store=True,
		copy=False
	)
	breadth_commission_achieved = fields.Float(
		string="Breadth Commission Achived",
		compute="_compute_commission_achieved",
		store=True,
		copy=False
	)
	kpi_commission_achieved = fields.Float(
		string="KPI Commission Achived",
		copy=False
	)
	deduction_commission_achieved = fields.Float(
		string="Deduction Commission Achived",
		copy=False
	)

	total_commission_achived = fields.Float(
		string="Total Commission Achived",
		copy=False,
		compute="_compute_commission_achieved",
		store=True
	)
	commission_priority = fields.Selection(
		selection=[
			('revenue_gp', 'Revenue/GP'),
			('breadth', 'Breadth'),
			('kpi', 'KPI'),
			('none', 'None')
		],
		default="revenue_gp",
		required=True
	)
	number_of_days_close = fields.Integer(
		string="Close After No. Of Days",
		default=10
	)
	auto_close_date = fields.Date(
		compute="_compute_auto_close_date",
		string="Auto Close Date",
		store=True
	)

	exception_state = fields.Selection(
		selection=[
			('no_exception', 'No Exception'),
			('exception', 'Exception'),
			('exception_approve_manager', 'Approved by Manager'),
			('exception_approve_hod', 'Approved by HOD'),
			('exception_approve_ceo', 'Approved by CEO'),
			('rejected', 'Rejected')
		],
		string="Exception Status",
		default='no_exception',
		tracking=True,
		copy=False
	)
	employee_manager_id = fields.Many2one(
		'hr.employee',
		string="Employee Manager",
	)
	department_manager_id = fields.Many2one(
		'hr.employee',
		string="Department Manager",
	)
	company_ceo_id = fields.Many2one(
		'res.users',
		string="CEO"
	)
	exception_reason = fields.Text(
		string="Exception Reason",
		copy=False,
		readonly=True
	)

	url = fields.Char('URL', compute='get_commission_url')



	@api.depends('user_id')
	def get_commission_url(self):
		for commission in self:
			ir_param = self.env['ir.config_parameter'].sudo()
			base_url = ir_param.get_param('web.base.url')
			action_id = self.env.ref('reddot_commission.action_commission_structure').id
			menu_id = self.env.ref('reddot_commission.menu_commission_structure').id
			company_id = self.user_id.company_id.id
			if base_url:
				base_url += '/web#id=%s&action=%s&model=%s&view_type=form&cids=%s&menu_id=%s' % (
				commission.id, action_id, 'commission.structure', company_id, menu_id)
			commission.url = base_url



	@api.depends('apply_commission_revenue', 'apply_commission_breadth', 'apply_commission_kpi', 'apply_commission_deduction',
					'revenue_gp_percentage', 'breadth_percentage', 'kpi_percentage','total_commission_amount', 'deduction_percentage')
	def _compute_all_amounts(self):
		for rec in self:
			rec.revenue_commission_amount = 0
			rec.breadth_commission_amount = 0
			rec.kpi_commission_amount = 0
			rec.deduction_commission_amount = 0
			if rec.apply_commission_revenue:
				rec.revenue_commission_amount = rec.total_commission_amount * rec.revenue_gp_percentage
			if rec.apply_commission_breadth:
			   rec.breadth_commission_amount = rec.total_commission_amount * rec.breadth_percentage
			if rec.apply_commission_kpi:
				rec.kpi_commission_amount = rec.total_commission_amount * rec.kpi_percentage
			if rec.apply_commission_deduction:
				rec.deduction_commission_amount = rec.total_commission_amount * rec.deduction_percentage

	@api.onchange(
		'start_year', 'start_month',
		'end_year', 'end_month',
	)
	def onchange_period(self):
		for record in self:
			if record.start_year and record.start_month:
				start_date = date(int(record.start_year), int(record.start_month), 1)
				record.start_date = start_date

			if record.end_year and record.end_month:
				end_date = date(
					int(record.end_year), int(record.end_month), 1
				) + relativedelta(day=31)
				record.end_date = end_date

	@api.onchange('period_type', 'start_month', 'start_year')
	def onchange_period_type(self):
		for record in self:
			if self.start_month and self.start_year:
				start_month = int(self.start_month)
				end_year = self.start_year
				month_plus_count = 0
				if record.period_type == 'monthly':
					month_plus_count = 0
				elif record.period_type == 'quarterly':
					month_plus_count = 2

				elif record.period_type == 'half_yearly':
					month_plus_count = 5

				elif record.period_type == 'yearly':
					month_plus_count = 11

				end_month = start_month + month_plus_count

				if end_month > 12:
					end_year = int(self.start_year) + 1
					end_month = end_month - 12
				self.update({
					'end_month': str(end_month),
					'end_year': str(end_year)
				})

	@api.constrains('apply_commission_revenue', 'apply_commission_breadth', 'apply_commission_kpi',
					'revenue_gp_percentage', 'breadth_percentage', 'kpi_percentage')
	def _check_percentage_sum(self):
		for record in self:
			# Initialize the sum
			percentage_sum = 0

			# Only add the percentages of the checked fields
			if record.apply_commission_revenue:
				_logger.error(f"rev perc: {record.revenue_gp_percentage}")
				percentage_sum += (record.revenue_gp_percentage*100)
			if record.apply_commission_breadth:
				_logger.error(f"breadth perc: {record.breadth_percentage}")
				percentage_sum += (record.breadth_percentage*100)
			if record.apply_commission_kpi:
				_logger.error(f"commission perc: {record.kpi_percentage}")
				percentage_sum += (record.kpi_percentage*100)

			# Check if the sum is 100
			if percentage_sum != 100:
				raise ValidationError(f"The sum of the percentages for the selected commissions must equal 100%. its at {percentage_sum}%")



	def check_user_manager(self, user_id):
		if user_id:
			result_dict = {}

			# Check for BU manager
			bu_managers = self.env['business.unit.managers'].sudo().search([('user_id', '=', user_id)])
			if bu_managers:
				bu_dict = {}
				for bu_manager in bu_managers:
					companies = bu_manager.company_ids.mapped('name')
					bu_dict[bu_manager.bu_id.name] = companies
				result_dict['bu'] = bu_dict

			# Check for BU Group manager
			bu_group_managers = self.env['business.unit.group.managers'].sudo().search([('user_id', '=', user_id)])
			if bu_group_managers:
				bu_group_dict = {}
				for bu_group_manager in bu_group_managers:
					companies = bu_group_manager.company_ids.mapped('name')
					bu_group_dict[bu_group_manager.bu_group_id.name] = companies
				result_dict['bu_group'] = bu_group_dict

			# Check for Company manager
			company_managers = self.env['res.company'].sudo().search([('company_manager_id', '=', user_id)])
			if company_managers:
				company_dict = {}
				for company in company_managers:
					company_dict[company.name] = company.name
				result_dict['companies'] = list(company_dict.values())

			# Check for Country Group manager
			country_group_managers = self.env['res.country.group'].sudo().search([('country_group_manager_id', '=', user_id)])
			if country_group_managers:
				country_group_dict = {}
				for country_group_manager in country_group_managers:
					countries = country_group_manager.country_ids.mapped('name')
					country_group_dict[country_group_manager.name] = countries
				result_dict['country_group'] = country_group_dict

			if result_dict:
				return result_dict

		return False



	@api.depends('number_of_days_close', 'end_date')
	def _compute_auto_close_date(self):
		for record in self:
			commission_close_days = 10
			if record.end_date:
				if record.number_of_days_close:
					commission_close_days = record.number_of_days_close
				record.auto_close_date = record.end_date + relativedelta(days=-commission_close_days)

	@api.depends(
		'commission_priority',
		'commission_structure_line_ids',
		'commission_structure_line_ids.commission_amount_achived',
		'breadth_commission_structure_line_ids',
		'commission_structure_line_ids.breadth_commission_amount_achived',
		'kpi_commission_achieved',
		'deduction_commission_achieved'
	)
	def _compute_commission_achieved(self):
		for record in self:
		# Compute individual commission achievements
			record.revenue_commission_achieved = sum(
				l.commission_amount_achived for l in record.commission_structure_line_ids
			)
			record.breadth_commission_achieved = sum(
				l.breadth_commission_amount_achived for l in record.breadth_commission_structure_line_ids
			)

			# Initialize total commission to zero
			total_commission_achived = 0.0

			# Check if any commission is achieved based on priority
			if (
				(record.commission_priority == 'revenue_gp' and record.revenue_commission_achieved > 0) or
				(record.commission_priority == 'breadth' and record.breadth_commission_achieved > 0) or
				(record.commission_priority == 'kpi' and record.kpi_commission_achieved > 0) or
				(record.commission_priority == 'none')
			):
				total_commission_achived = (
					record.revenue_commission_achieved +
					record.breadth_commission_achieved +
					record.kpi_commission_achieved
				)
			if record.deduction_commission_achieved > 0:
				total_commission_achived -= record.deduction_commission_achieved
			
			record.total_commission_achived = total_commission_achived

	@api.constrains('user_id', 'start_date', 'end_date')
	def _check_duplications(self):
		if self.user_id and self.start_date and self.end_date:
			exist_record = self.sudo().search([
				('user_id', '=', self.user_id.id),
				('start_date', '>=', self.start_date),
				('end_date', '<=', self.end_date),
				('id', '!=', self.id)
			])
			if exist_record:
				raise ValidationError(
					_('Commission structure already exists for same date period!')
				)

	def add_breadth_target(self, lines):
		for line in lines:
			self.breadth_commission_structure_line_ids += line
		


	@api.model_create_multi
	def create(self, vals_list):
		seq_obj = self.env['ir.sequence']
		for vals in vals_list:
			vals['name'] = seq_obj.next_by_code(
				'commission.structure',
				sequence_date=self.start_date
			)
		return super(CommissionStructure, self).create(vals_list)

	def action_structure_send(self):
		self.ensure_one()
		lang = self.env.context.get('lang')

		generated_report = self.env['ir.actions.report']._render_qweb_pdf(
			'reddot_commission.action_pdf_commission_structure', self.id)
		data_record = base64.b64encode(generated_report[0])
		ir_values = {
			'name': 'Commission_Structure',
			'type': 'binary',
			'datas': data_record,
			'store_fname': data_record,
			'mimetype': 'application/pdf',
			'res_model': 'commission.structure',
		}
		report_attachment = self.env['ir.attachment'].sudo().create(ir_values)
		email_template = self.env.ref('reddot_commission.mail_template_commission_structures')
		email_template.attachment_ids = [(4, report_attachment.id)]
		email_template.attachment_ids = [(5, 0, 0)]
		email_template.send_mail(self.id)

		self.write({'state': 'sent'})


	def action_approved(self):
		for record in self:
			record.action_generate_commission()
			record.update({
				'state': 'approved'
			})

	def action_validate(self):
		for record in self:
			record.update({
				'state': 'validate'
			})

	def action_in_payment(self):
		for record in self:
			record.update({
				'state': 'in_payment'
			})

	def action_rejected(self):
		for record in self:
			record.update({
				'state': 'rejected'
			})

	def action_paid(self):
		for record in self:
			record.update({
				'state': 'paid'
			})

	def action_reset_to_draft(self):
		for record in self:
			record.update({
				'state': 'draft'
			})

	def action_validate_kpi(self):
		for record in self:
			user_id = record.user_id

			employee_id = record.user_id.employee_id
			if not employee_id:
				employee_id = self.env['hr.employee'].sudo().search([
					('user_id', '=', record.user_id.id)
				], limit=1)

			if not employee_id:
				raise ValidationError(_("Sales Person don't have valid employee!"))

			if employee_id.parent_id.user_id != self.env.user:
				raise ValidationError(_("Only Managers can approve KPI commission!"))

			if all(l.manager_result == 'pass' for l in record.kpi_commission_structure_line_ids):
				record.kpi_commission_achieved = record.kpi_commission_amount


	def manager_approve_kpi(self):
		self.ensure_one()
		kpis = []
		for kpi in self.kpi_commission_structure_line_ids:
			line = {
				'kpi_line_id': kpi.id,
			}
			kpis.append((0, 0, line))
		wizard = self.env['kpi.commission.allocate'].create({
			'commission_structure_id': self.id,
			'line_ids': kpis
		})
		return {
			'name': f'Rate KPI',
			'type': 'ir.actions.act_window',
			'res_model': 'kpi.commission.allocate',
			'view_mode': 'form',
			'target': 'new',
			'res_id': wizard.id,
			}

	def manager_approve_deduction(self):
		self.ensure_one()
		deds = []
		for ded in self.ded_commission_structure_line_ids:
			line = {
				'ded_line_id': ded.id,
			}
			deds.append((0, 0, line))
		wizard = self.env['deduction.commission.allocate'].create({
			'commission_structure_id': self.id,
			'line_ids': deds
		})
		return {
			'name': f'Rate Deductions',
			'type': 'ir.actions.act_window',
			'res_model': 'deduction.commission.allocate',
			'view_mode': 'form',
			'target': 'new',
			'res_id': wizard.id,
			}

	def action_add_breath_targets(self):
		self.ensure_one()
		deds = []
		breadth_target = self.env['employee.target'].search([
			
			('start_date', '>=', self.start_date),
			('end_date', '<=', self.end_date),
			('target_type', '=', 'breadth'),
		])


		for ded in self.breadth_commission_structure_line_ids:
			vals = {
				'company_id': ded.company_id.id,
				'business_unit_id': ded.business_unit_id.id,
				'bu_group_id': ded.bu_group_id.id,
				'country_id': ded.country_id.id,
				'country_group_id': ded.country_group_id.id,
				'count': ded.breadth_target_count
			}
			deds.append((0,0,vals))
		wizard = self.env['employee.breadth.target.wizard'].create({
			'breadth_target_id': breadth_target.id,
			'commission_structure_id': self.id,
			'line_ids': deds
		})

		return {
		'name': f'Add Breadth Targets',
		'type': 'ir.actions.act_window',
		'res_model': 'employee.breadth.target.wizard',
		'view_mode': 'form',
		'target': 'new',
		'res_id': wizard.id,
		}


	def action_validate_deduction(self):
		for record in self:
			user_id = record.user_id

			employee_id = record.user_id.employee_id
			if not employee_id:
				employee_id = self.env['hr.employee'].sudo().search([
					('user_id', '=', record.user_id.id)
				], limit=1)

			if not employee_id:
				raise ValidationError(_("Sales Person don't have valid employee!"))

			if employee_id.parent_id.user_id != self.env.user:
				raise ValidationError(_("Only Managers can Rate Deductions!"))

			if all(l.manager_result == 'fail' for l in record.ded_commission_structure_line_ids):
				record.deduction_commission_achieved = record.deduction_commission_amount




	def action_raise_exception(self):
		self.ensure_one()
		commission_structure = self
		revenue_list = []
		breath_list = []
		kpi_list = []
		ded_list = []
		vals = {}
		for revenue in commission_structure.commission_structure_line_ids:
			revenue_dct = {
				'line_id': revenue.id,
				'revenue_wizard_target_archived': revenue.commission_amount_achived,
			}
			revenue_list.append((0, 0, revenue_dct))
		for breath in commission_structure.breadth_commission_structure_line_ids:
			breath_dct = {
				'line_id': breath.id,
				'breadth_wizard_target_archived': breath.breadth_commission_amount_achived,
			}
			breath_list.append((0, 0, breath_dct))

		for kpi in commission_structure.kpi_commission_structure_line_ids:
			kpi_dct = {
				'line_id': kpi.id,
				'manager_result': kpi.manager_result,
			}
			kpi_list.append((0, 0, kpi_dct))
		
		for ded in commission_structure.ded_commission_structure_line_ids:
			ded_dct = {
				'line_id': ded.id,
				'manager_result': ded.manager_result,
			}
			ded_list.append((0, 0, ded_dct))

		vals.update({
			'revenue_line_ids': revenue_list,
			'breadth_line_ids': breath_list,
			'kpi_line_ids': kpi_list,
			'ded_line_ids': ded_list
		})

		wizard = self.env['commission.structure.exception.reason.wizard'].create(vals)
		return {
			'name': f'Raise Exception',
			'type': 'ir.actions.act_window',
			'res_model': 'commission.structure.exception.reason.wizard',
			'view_mode': 'form',
			'target': 'new',
			'res_id': wizard.id,
			}


	def action_exception_approve_manager(self):
		for record in self:

			if self.env.user != self.employee_manager_id.user_id:
				raise ValidationError(_('Only employee manager can approve!'))

			for revenue in record.commission_structure_line_ids:
				if revenue.exception_state != 'no_exception':
					revenue.update({
						'exception_state': 'exception_approve_manager'
					})

			for breadth in record.breadth_commission_structure_line_ids:
				if breadth.exception_state != 'no_exception':
					breadth.update({
						'exception_state': 'exception_approve_manager'
					})
			for kpi in record.kpi_commission_structure_line_ids:
				if kpi.exception_state != 'no_exception':
					kpi.update({
						'exception_state': 'exception_approve_manager'
					})

			record.write({
				'exception_state': 'exception_approve_manager'
			})
	

	def action_exception_approve_hod(self):
		for record in self:

			if self.env.user != self.department_manager_id.user_id:
				raise ValidationError(_('Only department manager can approve!'))

			for revenue in record.commission_structure_line_ids:
				if revenue.exception_state != 'no_exception':
					revenue.update({
						'exception_state': 'exception_approve_hod'
					})

			for breadth in record.breadth_commission_structure_line_ids:
				if breadth.exception_state != 'no_exception':
					breadth.update({
						'exception_state': 'exception_approve_hod'
					})

			for kpi in record.kpi_commission_structure_line_ids:
				if kpi.exception_state != 'no_exception':
					kpi.update({
						'exception_state': 'exception_approve_hod'
					})
			record.write({
				'exception_state': 'exception_approve_hod'
			})

	def action_exception_approve_ceo(self):
		for record in self:

			if self.env.user != self.company_ceo_id:
				raise ValidationError(_('Only CEO can approve!'))

			for revenue in record.commission_structure_line_ids:
				if revenue.exception_state != 'no_exception':
					revenue.update({
						'commission_amount_achived': revenue.commission_to_be,
						'exception_state': 'exception_approve_ceo'
					})

			for breadth in record.breadth_commission_structure_line_ids:
				if breadth.exception_state != 'no_exception':
					breadth.update({
						'breadth_commission_amount_achived': breadth.commission_to_be,
						'exception_state': 'exception_approve_ceo'
					})

			for kpi in record.kpi_commission_structure_line_ids:
				if kpi.exception_state != 'no_exception':
					kpi.update({
						'manager_result': kpi.manager_result_to_be,
						'exception_state': 'exception_approve_ceo'
					})

			for ded in record.ded_commission_structure_line_ids:
				if kpi.exception_state != 'no_exception':
					kpi.update({
						'manager_result': kpi.manager_result_to_be,
						'exception_state': 'exception_approve_ceo'
					})

			record.write({
				'exception_state': 'exception_approve_ceo'
			})

	def cron_commission_close(self):
		commission_close_date = fields.Date.context_today(self)
		commission_to_close_ids = self.search([
			('auto_close_date', '<=', commission_close_date),
			('state', '=', 'approved')
		])
		if commission_to_close_ids:
			commission_to_close_ids.action_validate()

	@api.model
	def _update_lines(self, target_type="revenue_gp"):
		record = self

		target_field = "target_amount"
		line_field = "commission_structure_line_ids"
		commission_amount_field = "commission_amount_percentage"
		if target_type == "breadth":
			line_field = "breadth_commission_structure_line_ids"
			target_field = "breadth_target_count"
			commission_amount_field = "breadth_commission_percentage"

		record.update({
			line_field: [(5, 0, 0)]
		})

		contract_id = False

		lines = []
		#             employee_id = record.employee_id
		user_id = record.user_id

		employee_id = record.user_id.employee_id
		if not employee_id:
			employee_id = self.env['hr.employee'].sudo().search([
				('user_id', '=', record.user_id.id)
			], limit=1)

		if not employee_id:
			raise ValidationError(_("Sales Person don't have valid employee!"))

		if employee_id and record.commission_type:
			state_domain = [('state', 'in', ['open'])]
			contract_id = self.env['hr.contract'].search(
				[
					('employee_id', '=', employee_id.id),
				] + state_domain,
				limit=1
			)
			if not contract_id:
				raise ValidationError(_("Agent don't have valid contract!"))

			record.update({
				'employee_manager_id': employee_id.parent_id.id,
				'department_manager_id': employee_id.department_manager_id.id,
				'company_ceo_id': user_id.company_id.company_ceo_id.id,
			})
			common_domain = [
				('parent_id.start_date', '>=', record.start_date),
				('parent_id.end_date', '<=', record.end_date),
				('parent_id.state', '=', 'approved'),
				('parent_id.target_type', '=', target_type),
				('user_id', '=', record.user_id.id)
			]

			manager_domain = []

			field_read = False
			field_read_list = []
			if record.commission_type == 'self':
				field_read = 'business_unit_id'
				field_read_list = ['business_unit_id', 'company_id', 'country_id']

			elif record.commission_type == 'bu_wise':
				field_read = 'business_unit_id'
				field_read_list = ['business_unit_id']

			elif record.commission_type == 'bu_group_wise':
				field_read = 'bu_group_id'
				field_read_list = ['bu_group_id']

			elif record.commission_type == 'company_wise':
				field_read_list = ['company_id', 'bu_group_id', 'business_unit_id']
				field_read = 'company_id'


			elif record.commission_type == 'country_wise':
				field_read = 'country_id'
				field_read_list = ['country_id', 'bu_group_id', 'business_unit_id']


			elif record.commission_type == 'region_wise':
				field_read = 'country_group_id'
				field_read_list = ['country_group_id', 'business_unit_id']


			field_amount_read = 'target_revenue'
			if record.commission_measure_type == 'gross_profit':
				field_amount_read = 'target_gross_profit'

			if target_type == "breadth":
				field_amount_read = "target_breadth_count"

			period_count = 1

			if record.period_type == 'quarterly':
				period_count = 3
			elif record.period_type == 'half_yearly':
				period_count = 6
			elif record.period_type == 'yearly':
				period_count = 12
			if field_read and field_amount_read:
				domain = common_domain + manager_domain + [(field_amount_read, '!=', False)]
				read_result = self.env['employee.target.lines'].search_read(
					domain=domain,
					fields=field_read_list + [field_amount_read] + ['currency_id', 'threshold_id', 'id'],
				)
				read_dict = {}
				currency_id = 2
				threshold_id = None
				for res in read_result:
					key = []
					currency_id = res['currency_id'][0]
					threshold_id = res['threshold_id'][0]
					target_line_id = res['id']

					for field_r in field_read_list:
						if res[field_r]:
							key.append(field_r + '-' + str(res[field_r][0]))
						else:
							key.append(field_r + '-' + str(0))

					if tuple(key) not in read_dict:
						read_dict[tuple(key)] = 0
					amt = res[field_amount_read]


					read_dict[tuple(key)] += amt

				count = 0
				_logger.error(f"threshold: {threshold_id}")
				for read_key in read_dict:
					vals = {}
					for i in read_key:
						split_key = i.split('-')
						vals[split_key[0]] = int(split_key[1])
					vals.update({
						target_field: read_dict[read_key],
						'commission_amount': contract_id.commission_amount,
						'line_currency_id': currency_id,
						'threshold_id': threshold_id,
						'target_line_id': target_line_id

					})
					lines.append((0, 0, vals))
					count += 1

				if count:

					percentage = 100/count
					for line in lines:
						line[2].update({
							commission_amount_field: (percentage/100)
								})
					record.total_commission_amount = contract_id.commission_amount * period_count

		record.update({
			'commission_currency_id': contract_id and contract_id.commission_currency_id.id \
									  or self.user_id.company_id.currency_id.id,
			line_field: lines
		})

	@api.onchange('user_id', 'commission_type', 'commission_measure_type')
	def onchange_user_id(self):
		for record in self:
			if record.apply_commission_revenue:
				record._update_lines(target_type="revenue_gp")

			if record.apply_commission_breadth:
				record._update_lines(target_type="breadth")

	def _generate_self_commission_revenue(self):
		for line in self.commission_structure_line_ids:
			threshold_id = line.threshold_id
			target_achived = 0
			domain = [
				('move_id.invoice_date', '>=', self.start_date),
				('move_id.invoice_date', '<=', self.end_date),
				('move_id.state', '=', 'posted'),
				('move_id.is_transfer', '=', False),
				('move_type', 'in', ['out_invoice', 'out_refund'])
			]

			managers = self.check_user_manager(self.user_id.id)

			if not managers:
				domain = domain + [
					('move_id.user_id', '=', self.user_id.id)
				]

			if line.business_unit_id:
				domain = domain + [
					('product_id.bu_id', '=', line.business_unit_id.id)
				]



			if line.bu_group_id:
				domain = domain + [
					('product_id.bu_id.bu_group_id', '=', line.bu_group_id.id)
				]

			if line.company_id:
				domain = domain + [
					('move_id.company_id', '=', line.company_id.id)
				]

			if line.country_id:
				domain = domain + [
					('move_id.invoice_country_id', '=', line.country_id.id)
				]

			if line.country_group_id:
				domain = domain + [
					('move_id.invoice_country_id', 'in', line.country_group_id.country_ids.ids)
				]
			amount_field = 'price_subtotal'
			if self.commission_measure_type == 'gross_profit':
				amount_field = 'gp'

			read_records = self.env['account.move.line'].sudo().search(domain)
			target_achived = 0
			for read_record in read_records:
				if amount_field == 'gp':
					line_amount = read_record.gp
				else:
					line_amount = read_record.price_subtotal
				line_currency = self.env['res.currency'].browse(read_record.currency_id.id)
				line_company = self.env['res.company'].browse(read_record.company_id.id)
				amount = line_currency._convert(
					line_amount,
					line.line_currency_id,
					line_company,
					self.start_date,
				)
				if read_record.move_type == 'out_invoice':
					target_achived += abs(amount)
				elif read_record.move_type == 'out_refund':
					target_achived -= abs(amount)

			commission_amount_achived, target_percentage_achived = line._get_commission_percentage(
				target_achived,
				threshold_id
			)
			line.write({
				'target_achived': target_achived,
				'target_percentage_achived': target_percentage_achived,
				'commission_amount_achived': commission_amount_achived
			})
		return True

	def _generate_self_commission_breadth(self):
		# Breadth Commission Calculations
		for line in self.breadth_commission_structure_line_ids:
			threshold_id = line.threshold_id

			domain = [
				('move_id.invoice_date', '>=', self.start_date),
				('move_id.invoice_date', '<=', self.end_date),
				('move_id.state', '=', 'posted'),
				('move_id.is_transfer', '=', False),
				('move_type', 'in', ['out_invoice', 'out_refund'])
			]

			managers = False
			if line.commission_structure_id.user_id:
				managers = self.check_user_manager(line.commission_structure_id.user_id.id)

			if not managers:
				domain = domain + [
					('move_id.user_id', '=', self.user_id.id)
				]

			if line.business_unit_id:
				domain = domain + [
					('product_id.bu_id', '=', line.business_unit_id.id)
				]

			if line.bu_group_id:
				domain = domain + [
					('product_id.bu_id.bu_group_id', '=', line.bu_group_id.id)
				]

			if line.company_id:
				domain = domain + [
					('move_id.company_id', '=', line.company_id.id)
				]

			if line.country_id:
				domain = domain + [
					('move_id.invoice_country_id', '=', line.country_id.id)
				]

			if line.country_group_id:
				domain = domain + [
					('move_id.invoice_country_id', 'in', line.country_group_id.country_ids.ids)
				]

			read_records = self.env['account.move.line'].sudo().search(
				domain)

			# Initialize a dictionary to count partner occurrences and handle credits
			partner_counts = {}

			# Iterate over each record in the read group result
			for record in read_records:
				partner_id = record.partner_id.id
				move_type = record.move_type
				
				# Initialize count for partner if not present
				if partner_id not in partner_counts:
					partner_counts[partner_id] = 0

				# Increment or decrement based on invoice or credit note
				if move_type == 'out_invoice':
					partner_counts[partner_id] += 1
				elif move_type == 'out_refund':  # Assuming 'out_refund' is the credit note type
					partner_counts[partner_id] -= 1

			# Calculate the final unique partner count, adjusting for any negative values
			breadth_target_achieved = sum(1 for count in partner_counts.values() if count > 0)


			breadth_commission_amount_achived, breadth_target_percentage_achived = line._get_breadth_commission_percentage(
				breadth_target_achieved,
				threshold_id

			)

			line.write({
				'breadth_target_achived': breadth_target_achieved,
				'breadth_target_percentage_achived': breadth_target_percentage_achived,
				'breadth_commission_amount_achived': breadth_commission_amount_achived
			})
		return True

	def _generate_bu_wise_commission_revenue(self):
		for line in self.commission_structure_line_ids:
			threshold_id = line.threshold_id

			target_achived = 0


			domain = [
				('move_id.invoice_date', '>=', self.start_date),
				('move_id.invoice_date', '<=', self.end_date),
				('move_id.state', '=', 'posted'),
				('move_id.is_transfer', '=', False),
				('move_type', 'in', ['out_invoice', 'out_refund'])
			]

			if line.business_unit_id:
				domain = domain + [
					('product_id.bu_id', '=', line.business_unit_id.id)
				]

			managers = self.check_user_manager(self.user_id.id)

			if not managers:
				domain = domain + [
					('move_id.user_id', '=', self.user_id.id)
				]


			if line.bu_group_id:
				domain = domain + [
					('product_id.bu_id.bu_group_id', '=', line.bu_group_id.id)
				]

			if line.company_id:
				domain = domain + [
					('move_id.company_id', '=', line.company_id.id)
				]

			if line.country_id:
				domain = domain + [
					('move_id.invoice_country_id', '=', line.country_id.id)
				]

			if line.country_group_id:
				domain = domain + [
					('move_id.invoice_country_id', 'in', line.country_group_id.country_ids.ids)
				]
			amount_field = 'price_subtotal'
			if self.commission_measure_type == 'gross_profit':
				amount_field = 'gp'

			read_records = self.env['account.move.line'].sudo().search(domain)
			target_achived = 0
			for read_record in read_records:
				if amount_field == 'gp':
					line_amount = read_record.gp
				else:
					line_amount = read_record.price_subtotal
				line_currency = self.env['res.currency'].browse(read_record.currency_id.id)
				line_company = self.env['res.company'].browse(read_record.company_id.id)
				amount = line_currency._convert(
					line_amount,
					line.line_currency_id,
					line_company,
					self.start_date,
				)
				if read_record.move_type == 'out_invoice':
					target_achived += abs(amount)
				elif read_record.move_type == 'out_refund':
					target_achived -= abs(amount)
					
			commission_amount_achived, target_percentage_achived = line._get_commission_percentage(
				target_achived,
				threshold_id
			)
			line.write({
				'target_achived': target_achived,
				'target_percentage_achived': target_percentage_achived,
				'commission_amount_achived': commission_amount_achived
			})
		return True

	def _generate_bu_wise_commission_breadth(self):
		for line in self.breadth_commission_structure_line_ids:
			threshold_id = line.threshold_id


			target_achived = 0

			domain = [
				('move_id.invoice_date', '>=', self.start_date),
				('move_id.invoice_date', '<=', self.end_date),
				('move_id.state', '=', 'posted'),
				('move_id.is_transfer', '=', False),
				('move_type', 'in', ['out_invoice', 'out_refund'])
			]
			if line.business_unit_id:
				domain = domain + [
					('product_id.bu_id', '=', line.business_unit_id.id)
				]

			if line.bu_group_id:
				domain = domain + [
					('product_id.bu_id.bu_group_id', '=', line.bu_group_id.id)
				]

			if line.company_id:
				domain = domain + [
					('move_id.company_id', '=', line.company_id.id)
				]

			managers = self.check_user_manager(self.user_id.id)

			if not managers:
				domain = domain + [
					('move_id.user_id', '=', self.user_id.id)
				]

			if line.country_id:
				domain = domain + [
					('move_id.invoice_country_id', '=', line.country_id.id)
				]

			if line.country_group_id:
				domain = domain + [
					('move_id.invoice_country_id', 'in', line.country_group_id.country_ids.ids)
				]
			read_records = self.env['account.move.line'].sudo().search(
				domain)

			# Initialize a dictionary to count partner occurrences and handle credits
			partner_counts = {}

			# Iterate over each record in the read group result
			for record in read_records:
				partner_id = record.partner_id.id
				move_type = record.move_type
				
				# Initialize count for partner if not present
				if partner_id not in partner_counts:
					partner_counts[partner_id] = 0

				# Increment or decrement based on invoice or credit note
				if move_type == 'out_invoice':
					partner_counts[partner_id] += 1
				elif move_type == 'out_refund':  # Assuming 'out_refund' is the credit note type
					partner_counts[partner_id] -= 1

			# Calculate the final unique partner count, adjusting for any negative values
			breadth_target_achieved = sum(1 for count in partner_counts.values() if count > 0)


			breadth_commission_amount_achived, breadth_target_percentage_achived = line._get_breadth_commission_percentage(
				breadth_target_achieved,
				threshold_id
			)

			line.write({
				'breadth_target_achived': breadth_target_achieved,
				'breadth_target_percentage_achived': breadth_target_percentage_achived,
				'breadth_commission_amount_achived': breadth_commission_amount_achived
			})
		return True

	def _generate_bu_group_wise_commission_revenue(self):
		for line in self.commission_structure_line_ids:

			target_achived = 0
			domain = [
				('move_id.invoice_date', '>=', self.start_date),
				('move_id.invoice_date', '<=', self.end_date),
				('move_id.state', '=', 'posted'),
				('move_id.is_transfer', '=', False),
				('move_type', 'in', ['out_invoice', 'out_refund'])
			]

			if line.bu_group_id:
				domain = domain + [
					('product_id.bu_id.bu_group_id', '=', line.bu_group_id.id)
				]

			managers = self.check_user_manager(self.user_id.id)

			if not managers:
				domain = domain + [
					('move_id.user_id', '=', self.user_id.id)
				]

			if line.company_id:
				domain = domain + [
					('move_id.company_id', '=', line.company_id.id)
				]

			if line.country_id:
				domain = domain + [
					('move_id.invoice_country_id', '=', line.country_id.id)
				]

			if line.country_group_id:
				domain = domain + [
					('move_id.invoice_country_id', 'in', line.country_group_id.country_ids.ids)
				]
			amount_field = 'price_subtotal'
			if self.commission_measure_type == 'gross_profit':
				amount_field = 'gp'
			read_records = self.env['account.move.line'].sudo().search(domain)
			target_achived = 0
			for read_record in read_records:
				if amount_field == 'gp':
					line_amount = read_record.gp
				else:
					line_amount = read_record.price_subtotal
				line_currency = self.env['res.currency'].browse(read_record.currency_id.id)
				line_company = self.env['res.company'].browse(read_record.company_id.id)
				amount = line_currency._convert(
					line_amount,
					line.line_currency_id,
					line_company,
					self.start_date,
				)
				if read_record.move_type == 'out_invoice':
					target_achived += abs(amount)
				elif read_record.move_type == 'out_refund':
					target_achived -= abs(amount)

			commission_amount_achived, target_percentage_achived = line._get_commission_percentage(
				target_achived,
				threshold_id
			)
			line.write({
				'target_achived': target_achived,
				'target_percentage_achived': target_percentage_achived,
				'commission_amount_achived': commission_amount_achived
			})
		return True

	def _generate_bu_group_wise_commission_breadth(self):
		for line in self.breadth_commission_structure_line_ids:
			threshold_id = line.threshold_id

			target_achived = 0
			domain = [
				('move_id.invoice_date', '>=', self.start_date),
				('move_id.invoice_date', '<=', self.end_date),
				('move_id.state', '=', 'posted'),
				('move_id.is_transfer', '=', False),
				('move_type', 'in', ['out_invoice', 'out_refund'])
			]


			if line.bu_group_id:
				domain = domain + [
					('product_id.bu_id.bu_group_id', '=', line.bu_group_id.id)
				]

			managers = self.check_user_manager(self.user_id.id)

			if not managers:
				domain = domain + [
					('move_id.user_id', '=', self.user_id.id)
				]

			if line.company_id:
				domain = domain + [
					('move_id.company_id', '=', line.company_id.id)
				]

			if line.country_id:
				domain = domain + [
					('move_id.invoice_country_id', '=', line.country_id.id)
				]

			if line.country_group_id:
				domain = domain + [
					('move_id.invoice_country_id', 'in', line.country_group_id.country_ids.ids)
				]
			read_records = self.env['account.move.line'].sudo().search(
				domain)

			# Initialize a dictionary to count partner occurrences and handle credits
			partner_counts = {}

			# Iterate over each record in the read group result
			for record in read_records:
				partner_id = record.partner_id.id
				move_type = record.move_type
				
				# Initialize count for partner if not present
				if partner_id not in partner_counts:
					partner_counts[partner_id] = 0

				# Increment or decrement based on invoice or credit note
				if move_type == 'out_invoice':
					partner_counts[partner_id] += 1
				elif move_type == 'out_refund':  # Assuming 'out_refund' is the credit note type
					partner_counts[partner_id] -= 1

			# Calculate the final unique partner count, adjusting for any negative values
			breadth_target_achieved = sum(1 for count in partner_counts.values() if count > 0)


			breadth_commission_amount_achived, breadth_target_percentage_achived = line._get_breadth_commission_percentage(
				breadth_target_achieved,
				threshold_id
			)

			line.write({
				'breadth_target_achived': breadth_target_achieved,
				'breadth_target_percentage_achived': breadth_target_percentage_achived,
				'breadth_commission_amount_achived': breadth_commission_amount_achived
			})
		return True

	def _generate_company_wise_commission_revenue(self):
		for line in self.commission_structure_line_ids:
			threshold_id = line.threshold_id

			target_achived = 0
			domain = [
				('move_id.invoice_date', '>=', self.start_date),
				('move_id.invoice_date', '<=', self.end_date),
				('move_id.state', '=', 'posted'),
				('move_id.is_transfer', '=', False),
				('move_type', 'in', ['out_invoice', 'out_refund'])
			]

			managers = self.check_user_manager(self.user_id.id)

			if not managers:
				domain = domain + [
					('move_id.user_id', '=', self.user_id.id)
				]


			if line.company_id:
				domain = domain + [
					('move_id.company_id', '=', line.company_id.id)
				]

			if line.country_id:
				domain = domain + [
					('move_id.invoice_country_id', '=', line.country_id.id)
				]

			if line.country_group_id:
				domain = domain + [
					('move_id.invoice_country_id', 'in', line.country_group_id.country_ids.ids)
				]
			amount_field = 'price_subtotal'
			if self.commission_measure_type == 'gross_profit':
				amount_field = 'gp'
			read_records = self.env['account.move.line'].sudo().search(domain)
			target_achived = 0
			for read_record in read_records:
				if amount_field == 'gp':
					line_amount = read_record.gp
				else:
					line_amount = read_record.price_subtotal
				line_currency = self.env['res.currency'].browse(read_record.currency_id.id)
				line_company = self.env['res.company'].browse(read_record.company_id.id)
				amount = line_currency._convert(
					line_amount,
					line.line_currency_id,
					line_company,
					self.start_date,
				)
				if read_record.move_type == 'out_invoice':
					target_achived += abs(amount)
				elif read_record.move_type == 'out_refund':
					target_achived -= abs(amount)

			commission_amount_achived, target_percentage_achived = line._get_commission_percentage(
				target_achived,
				threshold_id
			)
			line.write({
				'target_achived': target_achived,
				'target_percentage_achived': target_percentage_achived,
				'commission_amount_achived': commission_amount_achived
			})
		return True

	def _generate_company_wise_commission_breadth(self):
		for line in self.breadth_commission_structure_line_ids:
			threshold_id = line.threshold_id

			target_achived = 0

			managers = self.check_user_manager(self.user_id.id)

			if not managers:
				domain = domain + [
					('move_id.user_id', '=', self.user_id.id)
				]

			domain = [
				('move_id.invoice_date', '>=', self.start_date),
				('move_id.invoice_date', '<=', self.end_date),
				('move_id.state', '=', 'posted'),
				('move_id.is_transfer', '=', False),
				('move_type', 'in', ['out_invoice', 'out_refund'])
			]

			if line.company_id:
				domain = domain + [
					('move_id.company_id', '=', line.company_id.id)
				]

			if line.country_id:
				domain = domain + [
					('move_id.invoice_country_id', '=', line.country_id.id)
				]

			if line.country_group_id:
				domain = domain + [
					('move_id.invoice_country_id', 'in', line.country_group_id.country_ids.ids)
				]
			read_records = self.env['account.move.line'].sudo().search(
				domain)

			# Initialize a dictionary to count partner occurrences and handle credits
			partner_counts = {}

			# Iterate over each record in the read group result
			for record in read_records:
				partner_id = record.partner_id.id
				move_type = record.move_type
				
				# Initialize count for partner if not present
				if partner_id not in partner_counts:
					partner_counts[partner_id] = 0

				# Increment or decrement based on invoice or credit note
				if move_type == 'out_invoice':
					partner_counts[partner_id] += 1
				elif move_type == 'out_refund':  # Assuming 'out_refund' is the credit note type
					partner_counts[partner_id] -= 1

			# Calculate the final unique partner count, adjusting for any negative values
			breadth_target_achieved = sum(1 for count in partner_counts.values() if count > 0)


			breadth_commission_amount_achived, breadth_target_percentage_achived = line._get_breadth_commission_percentage(
				breadth_target_achieved,
				threshold_id
			)

			line.write({
				'breadth_target_achived': breadth_target_achieved,
				'breadth_target_percentage_achived': breadth_target_percentage_achived,
				'breadth_commission_amount_achived': breadth_commission_amount_achived
			})
		return True

	def _generate_country_wise_commission_revenue(self):
		for line in self.commission_structure_line_ids:
			threshold_id = line.threshold_id
			target_achived = 0

			domain = [
				('move_id.invoice_date', '>=', self.start_date),
				('move_id.invoice_date', '<=', self.end_date),
				('move_id.state', '=', 'posted'),

				('move_id.is_transfer', '=', False),
			]

			managers = self.check_user_manager(self.user_id.id)

			if not managers:
				domain = domain + [
					('move_id.user_id', '=', self.user_id.id)
				]

			if line.country_id:
				domain = domain + [
					('move_id.invoice_country_id', '=', line.country_id.id)
				]
			if line.business_unit_id:
				domain = domain + [
					('product_id.bu_id', '=', line.business_unit_id.id)
				]

			if line.bu_group_id:
				domain = domain + [
					('product_id.bu_id.bu_group_id', '=', line.bu_group_id.id)
				]

			if line.country_group_id:
				domain = domain + [
					('move_id.invoice_country_id', 'in', line.country_group_id.country_ids.ids)
				]
			amount_field = 'price_subtotal'
			if self.commission_measure_type == 'gross_profit':
				amount_field = 'gp'
			read_records = self.env['account.move.line'].sudo().search(domain)
			target_achived = 0
			for read_record in read_records:
				if amount_field == 'gp':
					line_amount = read_record.gp
				else:
					line_amount = read_record.price_subtotal
				line_currency = self.env['res.currency'].browse(read_record.currency_id.id)
				line_company = self.env['res.company'].browse(read_record.company_id.id)
				amount = line_currency._convert(
					line_amount,
					line.line_currency_id,
					line_company,
					self.start_date,
				)
				if read_record.move_type == 'out_invoice':
					target_achived += abs(amount)
				elif read_record.move_type == 'out_refund':
					target_achived -= abs(amount)

			commission_amount_achived, target_percentage_achived = line._get_commission_percentage(
				target_achived,
				threshold_id
			)
			line.write({
				'target_achived': target_achived,
				'target_percentage_achived': target_percentage_achived,
				'commission_amount_achived': commission_amount_achived
			})
		return True

	def _generate_country_wise_commission_breadth(self):
		for line in self.breadth_commission_structure_line_ids:
			threshold_id = line.threshold_id

			target_achived = 0
			domain = [
				('move_id.invoice_date', '>=', self.start_date),
				('move_id.invoice_date', '<=', self.end_date),
				('move_id.state', '=', 'posted'),
				('move_id.is_transfer', '=', False),
				('move_type', 'in', ['out_invoice', 'out_refund'])
			]

			if line.country_id:
				domain = domain + [
					('move_id.invoice_country_id', '=', line.country_id.id)
				]

			if line.business_unit_id:
				domain = domain + [
					('product_id.bu_id', '=', line.business_unit_id.id)
				]

			if line.bu_group_id:
				domain = domain + [
					('product_id.bu_id.bu_group_id', '=', line.bu_group_id.id)
				]

			if line.country_group_id:
				domain = domain + [
					('move_id.invoice_country_id', 'in', line.country_group_id.country_ids.ids)
				]

			managers = self.check_user_manager(self.user_id.id)

			if not managers:
				domain = domain + [
					('move_id.user_id', '=', self.user_id.id)
				]

			read_records = self.env['account.move.line'].sudo().search(
				domain)

			# Initialize a dictionary to count partner occurrences and handle credits
			partner_counts = {}

			# Iterate over each record in the read group result
			for record in read_records:
				partner_id = record.partner_id.id
				move_type = record.move_type
				
				# Initialize count for partner if not present
				if partner_id not in partner_counts:
					partner_counts[partner_id] = 0

				# Increment or decrement based on invoice or credit note
				if move_type == 'out_invoice':
					partner_counts[partner_id] += 1
				elif move_type == 'out_refund':  # Assuming 'out_refund' is the credit note type
					partner_counts[partner_id] -= 1

			# Calculate the final unique partner count, adjusting for any negative values
			breadth_target_achieved = sum(1 for count in partner_counts.values() if count > 0)


			breadth_commission_amount_achived, breadth_target_percentage_achived = line._get_breadth_commission_percentage(
				breadth_target_achieved,
				threshold_id
			)

			line.write({
				'breadth_target_achived': breadth_target_achieved,
				'breadth_target_percentage_achived': breadth_target_percentage_achived,
				'breadth_commission_amount_achived': breadth_commission_amount_achived
			})
		return True

	def _generate_region_wise_commission_revenue(self):
		for line in self.commission_structure_line_ids:
			threshold_id = line.threshold_id
			target_achived = 0
			domain = [
				('move_id.invoice_date', '>=', self.start_date),
				('move_id.invoice_date', '<=', self.end_date),
				('move_id.state', '=', 'posted'),
				('move_id.is_transfer', '=', False),
				('move_type', 'in', ['out_invoice', 'out_refund'])
			]

			if line.country_group_id:
				domain = domain + [
					('move_id.invoice_country_id', 'in', line.country_group_id.country_ids.ids)
				]

			managers = self.check_user_manager(self.user_id.id)

			if not managers:
				domain = domain + [
					('move_id.user_id', '=', self.user_id.id)
				]

			if line.business_unit_id:
				domain = domain + [
					('product_id.bu_id', '=', line.business_unit_id.id)
				]


			amount_field = 'price_subtotal'
			if self.commission_measure_type == 'gross_profit':
				amount_field = 'gp'
			read_records = self.env['account.move.line'].sudo().search(domain)
			target_achived = 0
			for read_record in read_records:
				if amount_field == 'gp':
					line_amount = read_record.gp
				else:
					line_amount = read_record.price_subtotal
				line_currency = self.env['res.currency'].browse(read_record.currency_id.id)
				line_company = self.env['res.company'].browse(read_record.company_id.id)
				amount = line_currency._convert(
					line_amount,
					line.line_currency_id,
					line_company,
					self.start_date,
				)
				if read_record.move_type == 'out_invoice':
					target_achived += abs(amount)
				elif read_record.move_type == 'out_refund':
					target_achived -= abs(amount)

			commission_amount_achived, target_percentage_achived = line._get_commission_percentage(
				target_achived,
				threshold_id
			)
			line.write({
				'target_achived': target_achived,
				'target_percentage_achived': target_percentage_achived,
				'commission_amount_achived': commission_amount_achived
			})
		return True

	def _generate_region_wise_commission_breadth(self):
		for line in self.breadth_commission_structure_line_ids:
			threshold = line.threshold_id
			target_achived = 0
			domain = [
				('move_id.invoice_date', '>=', self.start_date),
				('move_id.invoice_date', '<=', self.end_date),
				('move_id.state', '=', 'posted'),
				('move_id.is_transfer', '=', False),
				('move_type', 'in', ['out_invoice', 'out_refund'])
			]

			if line.country_group_id:
				domain = domain + [
					('move_id.invoice_country_id', 'in', line.country_group_id.country_ids.ids)
				]

			managers = self.check_user_manager(self.user_id.id)

			if not managers:
				domain = domain + [
					('move_id.user_id', '=', self.user_id.id)
				]

			if line.business_unit_id:
				domain = domain + [
					('product_id.bu_id', '=', line.business_unit_id.id)
				]

			if line.bu_group_id:
				domain = domain + [
					('product_id.bu_id.bu_group_id', '=', line.bu_group_id.id)
				]


			amount_field = 'price_subtotal'
			if self.commission_measure_type == 'gross_profit':
				amount_field = 'gp'
			read_records = self.env['account.move.line'].sudo().search(
				domain)

			# Initialize a dictionary to count partner occurrences and handle credits
			partner_counts = {}

			# Iterate over each record in the read group result
			for record in read_records:
				partner_id = record.partner_id.id
				move_type = record.move_type
				
				# Initialize count for partner if not present
				if partner_id not in partner_counts:
					partner_counts[partner_id] = 0

				# Increment or decrement based on invoice or credit note
				if move_type == 'out_invoice':
					partner_counts[partner_id] += 1
				elif move_type == 'out_refund':  # Assuming 'out_refund' is the credit note type
					partner_counts[partner_id] -= 1

			# Calculate the final unique partner count, adjusting for any negative values
			breadth_target_achieved = sum(1 for count in partner_counts.values() if count > 0)
			breadth_commission_amount_achived, breadth_target_percentage_achived = line._get_breadth_commission_percentage(
				breadth_target_achieved,
				threshold_id
			)

			line.write({
				'breadth_target_achived': breadth_target_achieved,
				'breadth_target_percentage_achived': breadth_target_percentage_achived,
				'breadth_commission_amount_achived': breadth_commission_amount_achived
			})

		return True

	@api.constrains('breadth_commission_structure_line_ids', 'apply_commission_breadth')
	def check_amount_match(self):
		for rec in self:
			if rec.apply_commission_breadth and rec.breadth_commission_structure_line_ids:
				commission_amount = sum([breadth.breadth_commission_amount for breadth in rec.breadth_commission_structure_line_ids])
				if int(commission_amount) != int(rec.breadth_commission_amount):
					raise ValidationError(_(f"Breadth Percent Lines is not equal to 100% {commission_amount}"))

	@api.constrains('commission_structure_line_ids', 'apply_commission_revenue')
	def check_rev_amount_match(self):
		for rec in self:
			if rec.apply_commission_revenue and rec.commission_structure_line_ids:
				commission_amount = sum([revenue.commission_amount for revenue in rec.commission_structure_line_ids])
				if int(commission_amount) != int(rec.revenue_commission_amount):
					raise ValidationError(_(f"Revenue Percent Lines is not equal to 100%: SUM: {commission_amount}"))



	def action_generate_commission(self):
		for record in self:
			start_date = self.start_date
			end_date = self.end_date

			employee_id = record.user_id.employee_id
			if not employee_id:
				employee_id = self.env['hr.employee'].sudo().search([
					('user_id', '=', record.user_id.id)
				], limit=1)

			if not employee_id:
				raise ValidationError(_("Sales Person don't have valid employee!"))

			if not record.employee_manager_id:
				record.update({
					'employee_manager_id': employee_id.parent_id.id
				})

			if not record.department_manager_id:
				record.update({
					'department_manager_id': employee_id.department_manager_id.id
				})

			if not record.company_ceo_id:
				record.update({
					'company_ceo_id': record.user_id.company_id.company_ceo_id.id
				})

			if record.commission_type == 'self':
				if self.apply_commission_revenue:
					record._generate_self_commission_revenue()
				if self.apply_commission_breadth:
					record._generate_self_commission_breadth()

			elif record.commission_type == 'bu_wise':
				if self.apply_commission_revenue:
					record._generate_bu_wise_commission_revenue()
				if self.apply_commission_breadth:
					record._generate_bu_wise_commission_breadth()

			elif record.commission_type == 'bu_group_wise':
				if self.apply_commission_revenue:
					record._generate_bu_group_wise_commission_revenue()
				if self.apply_commission_breadth:
					record._generate_bu_group_wise_commission_breadth()

			elif record.commission_type == 'company_wise':
				if self.apply_commission_revenue:
					record._generate_company_wise_commission_revenue()
				if self.apply_commission_breadth:
					record._generate_company_wise_commission_breadth()

			elif record.commission_type == 'country_wise':
				if self.apply_commission_revenue:
					record._generate_country_wise_commission_revenue()
				if self.apply_commission_breadth:
					record._generate_country_wise_commission_breadth()

			elif record.commission_type == 'region_wise':
				if self.apply_commission_revenue:
					record._generate_region_wise_commission_revenue()
				if self.apply_commission_breadth:
					record._generate_region_wise_commission_breadth()

	def unlink(self):
		for rec in self:
			if rec.state != 'draft':
				raise ValidationError(_('You can not delete non-draft commissions!'))
		return super(CommissionStructure, self).unlink()


class CommissionStructureLine(models.Model):
	_name = 'commission.structure.line'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = 'Commission Structure Line'

	name = fields.Char(
		'Name',
	)
	company_id = fields.Many2one(
		'res.company',
		string="Company",
	)
	business_unit_id = fields.Many2one(
		'business.unit',
		string='Business Unit',
	)
	bu_group_id = fields.Many2one(
		'business.unit.group',
		string="BU Group",
	)
	country_id = fields.Many2one(
		'res.country',
		string='Country',
	)
	country_group_id = fields.Many2one(
		'res.country.group',
		string='Country Group',
	)
	target_amount = fields.Float(
		string="Target"
	)
	target_revenue = fields.Float(
		string="Target Revenue"
	)
	target_gross_profit = fields.Float(
		string="Gross Profit Target"
	)
	commission_structure_id = fields.Many2one(
		'commission.structure',
		string='Commission Structure',
	)
	commission_amount = fields.Float(
		string="Split Commission Amount",
		compute="_compute_rev_split_amount",
		store=True
	)
	target_percentage_achived = fields.Float(
		string="Target Achived(%)"
	)
	target_achived = fields.Float(
		string="Target Achived"
	)
	commission_amount_achived = fields.Float(
		string="Commission Achived"

	)
	commission_amount_percentage = fields.Float(
		string="Commission Percentage(%)"
	)
	# Breadth
	breadth_commission_structure_id = fields.Many2one(
		'commission.structure',
		string='Breadth Commission Structure',
	)
	breadth_target_count = fields.Float(
		string="Target"
	)
	breadth_commission_amount = fields.Float(
		string="Split Commission Amount",
		compute="_compute_breadth_split_amount",
		store=True
	)
	breadth_commission_percentage = fields.Float(
		string="Commission Percentage(%)"
	)
	breadth_target_percentage_achived = fields.Float(
		string="Target Achived(%)"
	)
	breadth_target_achived = fields.Float(
		string="Target Achived"
	)
	breadth_commission_amount_achived = fields.Float(
		string="Commission Achived"
	)
	commission_currency_id = fields.Many2one(
		'res.currency',
		string='Currency',
		compute='_compute_commission_currency_id',
		store=True
	)

	line_currency_id = fields.Many2one(
		'res.currency',
		string="Currency",
		default = lambda self: self.env.ref('base.USD')
	)
	is_exception = fields.Boolean(
		string="Exception?",
	)
	exception_reason = fields.Text(
		string="Reason"
	)
	exception_state = fields.Selection(
		selection=[
			('no_exception', 'No Exception'),
			('exception', 'Exception'),
			('exception_approve_manager', 'Approved by Manager'),
			('exception_approve_hod', 'Approved by HOD'),
			('exception_approve_ceo', 'Approved by CEO'),
			('rejected', 'Rejected')
		],
		string="Exception Status",
		default='no_exception',
		tracking=True,
		copy=False
	)
	commission_to_be = fields.Float(
		string="Commission To Be"
	)
	threshold_id = fields.Many2one('threshold.configuration', 'Threshold')
	revenue_commission_measure_type = fields.Selection(related='commission_structure_id.commission_measure_type')
	breadth_commission_measure_type = fields.Selection(related='breadth_commission_structure_id.commission_measure_type')
	commission_measure_type = fields.Selection(
		selection=[
			('revenue', 'Revenue'),
			('gross_profit', 'Gross Profit'),
		],
		string="Commission Measure Type",
		compute="_compute_measure_type",
		readonly=False,
		store="True",
	)
	target_line_id = fields.Many2one('employee.target.lines', string='Target Line')


	@api.depends('breadth_commission_measure_type', 'revenue_commission_measure_type')
	def _compute_measure_type(self):
		for rec in self:
			if rec.revenue_commission_measure_type:
				if rec.revenue_commission_measure_type != 'both':
					rec.commission_measure_type = rec.revenue_commission_measure_type
				else:
					rec.commission_measure_type = 'revenue'

			elif rec.breadth_commission_measure_type:
				if rec.breadth_commission_measure_type != 'both':
					rec.commission_measure_type = rec.breadth_commission_measure_type
				else:
					rec.commission_measure_type = 'revenue'

	@api.onchange('commission_measure_type')
	def recompute_commission(self):
		for rec in self:
			if rec.commission_measure_type == 'revenue':
				rec.target_amount = rec.target_line_id.target_revenue
			elif rec.commission_measure_type == 'gross_profit':
				rec.target_amount = rec.target_line_id.target_gross_profit

			



	@api.depends('commission_amount_percentage', 'commission_structure_id')
	def _compute_rev_split_amount(self):
		for rec in self:
			rec.commission_amount = 0
			if rec.commission_amount_percentage:
				rec.commission_amount = rec.commission_amount_percentage * rec.commission_structure_id.revenue_commission_amount


	@api.depends('breadth_commission_percentage', 'breadth_commission_structure_id')
	def _compute_breadth_split_amount(self):
		for rec in self:
			rec.breadth_commission_amount = 0
			if rec.breadth_commission_percentage:
				rec.breadth_commission_amount = rec.breadth_commission_percentage * rec.breadth_commission_structure_id.breadth_commission_amount


	@api.depends('breadth_commission_structure_id', 'commission_structure_id')
	def _compute_commission_currency_id(self):
		for line in self:
			if line.breadth_commission_structure_id:
				line.commission_currency_id = line.breadth_commission_structure_id.commission_currency_id.id
			else:
				line.commission_currency_id = line.commission_structure_id.commission_currency_id.id

	@api.onchange('business_unit_id')
	def onchange_business_unit(self):
		for line in self:
			line.bu_group_id = line.business_unit_id.bu_group_id.id

	@api.model
	def _get_target_achived_amounts(self):
		target_achived = 0
		domain = [
			('move_id.invoice_date', '>=', self.commission_structure_id.start_date),
			('move_id.invoice_date', '<=', self.commission_structure_id.end_date),
			('move_id.state', '=', 'posted'),
			('move_id.user_id', '=', self.commission_structure_id.user_id.id),
			('move_id.is_transfer', '=', False),
		]
		if self.business_unit_id:
			domain = domain + [('product_id.bu_id', '=', self.business_unit_id.id)]

		if self.bu_group_id:
			domain = domain + [('product_id.bu_id.bu_group_id', '=', self.bu_group_id.id)]

		if self.company_id:
			domain = domain + [('move_id.company_id', '=', self.company_id.id)]

		if self.country_id:
			domain = domain + [('move_id.invoice_country_id', '=', self.country_id.id)]

		if self.country_group_id:
			domain = domain + [('move_id.invoice_country_id', 'in', self.country_group_id.country_ids.ids)]
		amount_field = 'price_subtotal'
		if self.commission_measure_type == 'gross_profit':
			amount_field = 'gp'
		read_records = self.env['account.move.line'].sudo().read_group(
			domain,
			[amount_field],
			['product_id']
		)
		price_total_amt = 0
		for read_record in read_records:
			target_achived += read_record[amount_field]
		return target_achived

	@api.model
	def _get_breadth_commission_percentage(self, target_achived, threshold_id):
		target_amount = self.breadth_target_count
		target_percentage = (100.0 * target_achived) / target_amount

		commission_percentage = 0
		target_commission_percent_line = threshold_id.line_ids.filtered(
			lambda i: i.from_percentage <= target_percentage and i.to_percentage >= target_percentage
		).sorted(key=lambda i: i.from_percentage)
		if target_commission_percent_line:
			target_commission_percent_line = target_commission_percent_line[0]
			commission_percentage = target_commission_percent_line.commission_percentage
			if target_commission_percent_line.is_prorata:
				commission_percentage = target_percentage

		commission_amount_achived = (
											self.breadth_commission_amount * commission_percentage
									) / 100.0

		return commission_amount_achived, target_percentage

	@api.model
	def _get_commission_percentage(self, target_achived, threshold_id):
		target_amount = self.target_amount
		target_percentage = (100.0 * target_achived) / target_amount

		commission_percentage = 0
		target_commission_percent_line = threshold_id.line_ids.filtered(
			lambda i: i.from_percentage <= target_percentage and i.to_percentage >= target_percentage
		).sorted(key=lambda i: i.from_percentage)
		if target_commission_percent_line:
			target_commission_percent_line = target_commission_percent_line[0]
			commission_percentage = target_commission_percent_line.commission_percentage
			if target_commission_percent_line.is_prorata:
				commission_percentage = target_percentage

		commission_amount_achived = (
											self.commission_amount * commission_percentage
									) / 100.0

		return commission_amount_achived, target_percentage

	def name_get(self):
		result = []
		for line in self:
			if line != False:
				name_list = []
				if line.country_group_id:
					name_list.append(line.country_group_id.name)

				if line.country_id:
					name_list.append(line.country_id.name)

				if line.company_id:
					name_list.append(line.company_id.name)

				if line.bu_group_id:
					name_list.append(line.bu_group_id.name)

				if line.business_unit_id:
					name_list.append(line.business_unit_id.name)

				name = '-'.join(name_list)
				result.append((line._origin.id, name))
		return result







class CommissionStructureLineKPI(models.Model):
	_name = 'commission.structure.kpi.line'
	_description = 'Commission Structure KPI Line'

	name = fields.Text(
		'KPI Description',
		compute="_compute_name",
		store=True
	)

	kpi_comm_id = fields.Many2one('commission.kpi.category', string='Kpi', required=True)
	user_result = fields.Selection(
		selection=[
			('todo', 'Todo'),
			('pass', 'Pass'),
			('fail', 'Fail'),
		],
		default="todo",
	)
	manager_result = fields.Selection(
		selection=[
			('todo', 'Todo'),
			('pass', 'Pass'),
			('fail', 'Fail'),
		],
		default="todo",
	)

	manager_result_to_be = fields.Selection(
		selection=[
			('todo', 'Todo'),
			('pass', 'Pass'),
			('fail', 'Fail'),
		],
	)
	comment = fields.Text(
		string="Comment"
	)
	commission_structure_id = fields.Many2one(
		'commission.structure',
		string='Commission Structure',
	)

	is_exception = fields.Boolean(
		string="Exception?",
	)

	exception_reason = fields.Text(
		string="Reason"
	)

	exception_state = fields.Selection(
		selection=[
			('no_exception', 'No Exception'),
			('exception', 'Exception'),
			('exception_approve_manager', 'Approved by Manager'),
			('exception_approve_hod', 'Approved by HOD'),
			('exception_approve_ceo', 'Approved by CEO'),
			('rejected', 'Rejected')
		],
		string="Exception Status",
		default='no_exception',
		tracking=True,
		copy=False
	)


	@api.depends('commission_structure_id', 'kpi_comm_id')
	def _compute_name(self):
		for rec in self:
			rec.name = ''
			if rec.commission_structure_id and rec.kpi_comm_id:
				rec.name = rec.commission_structure_id.name + ' - ' + rec.kpi_comm_id.name



class CommissionStructureLineDeduction(models.Model):
	_name = 'commission.structure.deduction.line'
	_description = 'Commission Structure Deduction Line'

	name = fields.Text(
		'Deduction Description',
		compute="_compute_name",
		store=True
	)

	ded_comm_id = fields.Many2one('commission.ded.category', string='Deduction', required=True)
	user_result = fields.Selection(
		selection=[
			('todo', 'Todo'),
			('pass', 'Pass'),
			('fail', 'Fail'),
		],
		default="todo",
	)
	manager_result = fields.Selection(
		selection=[
			('todo', 'Todo'),
			('pass', 'Pass'),
			('fail', 'Fail'),
		],
		default="todo",
	)

	manager_result_to_be = fields.Selection(
		selection=[
			('todo', 'Todo'),
			('pass', 'Pass'),
			('fail', 'Fail'),
		],
	)
	comment = fields.Text(
		string="Comment"
	)
	commission_structure_id = fields.Many2one(
		'commission.structure',
		string='Commission Structure',
	)

	is_exception = fields.Boolean(
		string="Exception?",
	)

	exception_reason = fields.Text(
		string="Reason"
	)

	exception_state = fields.Selection(
		selection=[
			('no_exception', 'No Exception'),
			('exception', 'Exception'),
			('exception_approve_manager', 'Approved by Manager'),
			('exception_approve_hod', 'Approved by HOD'),
			('exception_approve_ceo', 'Approved by CEO'),
			('rejected', 'Rejected')
		],
		string="Exception Status",
		default='no_exception',
		tracking=True,
		copy=False
	)


	@api.depends('commission_structure_id', 'ded_comm_id')
	def _compute_name(self):
		for rec in self:
			rec.name = ''
			if rec.commission_structure_id and rec.ded_comm_id:
				rec.name = rec.commission_structure_id.name + ' - ' + rec.ded_comm_id.name

