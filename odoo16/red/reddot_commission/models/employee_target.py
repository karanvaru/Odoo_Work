# -*- coding: utf-8 -*-
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.fields import Command
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

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


class EmployeeTargets(models.Model):
	_name = 'employee.target'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = 'Employee Target'

	@api.model
	def _get_year_options(self):
		years = []
		for i in range(2024, 2101):
			years.append((str(i), str(i)))
		return years

	name = fields.Char(
		'Name',
		copy=False
	)
	start_year = fields.Selection(
		selection="_get_year_options",
		default="2024",
		string="Start Year",
		required=True,
		copy=False
	)

	end_year = fields.Selection(
		selection="_get_year_options",
		default="2024",
		string="End Year",
#         required=True,
		copy=False
	)

	threshold_id = fields.Many2one('threshold.configuration', 'Threshold', required=True)


	start_month = fields.Selection(
		selection=MONTH_SELECTION,
		string="Start Month",
#         required=True,
		copy=False
	)

	end_month = fields.Selection(
		selection=MONTH_SELECTION,
		string="End Month",
#         required=True,
		copy=False
	)
	state = fields.Selection(
		selection=[
			('draft', 'Draft'),
			('approved', 'Approved')
		],
		string="Status",
		default="draft",
		copy=False
	)
	user_id = fields.Many2one(
		'res.users',
		default=lambda self: self._uid,
		readonly=True,
		copy=False
	)
	line_ids = fields.One2many(
		'employee.target.lines',
		'parent_id',
		string="Lines",
	)
	date = fields.Date(
		string="Date",
		default=lambda self: fields.Date.context_today(self),
		readonly=True,
		copy=False
	)
	target_type = fields.Selection(
		selection=[
			('revenue_gp', 'Revenue/GP'),
			('breadth', 'Breadth'),
		],
		default="revenue_gp",
		string="Target Type"
	)
	
	start_date = fields.Date(
		string="Start Date",
		copy=False
	)
	end_date = fields.Date(
		string="End Date",
		copy=False
	)

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
				end_date = date(int(record.end_year), int(record.end_month), 1) + relativedelta(day=31)
				record.end_date = end_date

	@api.constrains('user_id', 'start_date', 'end_date')
	def _check_duplications(self):
		for record in self:
			if record.user_id and record.start_date and record.end_date:
				exist_record = self.sudo().search([
					('user_id', '=', record.user_id.id),
					('start_date', '>=', record.start_date),
					('end_date', '<=', record.end_date),
					('id', '!=', record.id),
					('target_type', '=', record.target_type)
				])
				if exist_record:
					raise ValidationError(
						_('Commission structure already exists for same date period!')
					)

	def copy_data(self, default=None):
		if default is None:
			default = {}
		if 'line_ids' not in default:
			default['line_ids'] = [
				Command.create(line.copy_data()[0])
				for line in self.line_ids
			]
		return super().copy_data(default)

	def action_confirm(self):
		for record in self:
			record.write({
				'state': 'approved',
			})

	def action_reset_to_draft(self):
		for record in self:
			record.update({
				'state': 'draft'
			})

	def unlink(self):
		for rec in self:
			if rec.state != 'draft':
				raise ValidationError(_('You can not delete non-draft commissions!'))
		return super(EmployeeTargets, self).unlink()


class EmployeeTargetsLines(models.Model):
	_name = 'employee.target.lines'

	parent_id = fields.Many2one(
		'employee.target',
		string="Parent"
	)
	user_id = fields.Many2one(
		'res.users',
		string="SalesPerson",
		required=True
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

	threshold_id = fields.Many2one('threshold.configuration', related='parent_id.threshold_id')

	target_revenue = fields.Float(
		string="Revenue Target"
	)
	target_gross_profit = fields.Float(
		string="Gross Profit Target"
	)
	target_breadth_count = fields.Float(
		string="Breadth Target"
	)
	currency_id = fields.Many2one(
		'res.currency',
		string='Currency',
	)

	@api.onchange('business_unit_id')
	def onchange_business_unit(self):
		for line in self:
			line.bu_group_id = line.business_unit_id.bu_group_id.id
	
	@api.onchange('user_id')
	def onchange_user(self):
		for line in self:
			line.currency_id = line.user_id.company_id.currency_id.id
	
	@api.model
	def create(self, vals):
		id = super(EmployeeTargetsLines, self).create(vals)
		if not id.currency_id and id.user_id:
			id.currency_id = id.user_id.company_id.currency_id.id
		return id
