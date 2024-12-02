# -*- coding: utf-8 -*-
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

from odoo import models, fields, api
from odoo.fields import Command


class ThresholdConfiguration(models.Model):
	_name = 'threshold.configuration'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description="Thresold Template"

	name = fields.Char(
		'Name',
		required=True,
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
		default=lambda self:self._uid,
		readonly=True
	)
	line_ids = fields.One2many(
		"threshold.configuration.lines",
		'parent_id',
		string="Lines"
	)
	date = fields.Date(
		string="Date",
		default=lambda self: fields.Date.context_today(self),
		readonly=True
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
		return super(ThresholdConfiguration, self).unlink()
	

class ThresholdConfigurationLines(models.Model):
	_name = 'threshold.configuration.lines'
	_description="Thresold Template Lines"

	from_percentage = fields.Float(
		string="From(%)"
	)
	to_percentage = fields.Float(
		string="To(%)"
	)
	commission_percentage = fields.Float(
		string="Commission(%)"
	)
	parent_id = fields.Many2one(
		'threshold.configuration',
		string="Parent",
		copy=False,
	)
	is_prorata = fields.Boolean(
		string="Prorata?"
	)
