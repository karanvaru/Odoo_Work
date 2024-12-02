# -*- coding: utf-8 -*-

from odoo import fields, models


class SetMarkupValue(models.Model):
	_name = "set.markup.value"
	_description = "Set Markup Value"

	markup_perc = fields.Float(string="Markup %")
	
	def action_set_markup(self):
		res = self.env['cost.estimation'].browse(self._context.get('active_ids'))
		for line in res.cost_estimation_line:
			markup_value = (line.cost_total_include_taxes * self.markup_perc) / 100
			line.update({'markup_value': markup_value, 'markup_perc': self.markup_perc})
		# for rec in res.products_line:
		# 	markup_value = (rec.total_cost * self.markup_perc) / 100
		# 	rec.update({'margin': self.markup_perc, 'markup_value': markup_value})
