from odoo import models, fields, api


class CommissionStructureExceptionReasonWizard(models.TransientModel):
	_name = 'commission.structure.exception.reason.wizard'
	_description = "Exception Reason Wizard"

	revenue_line_ids = fields.One2many(
		"commission.exception.wizard.revenue.line",
		'revenue_commission_structure_exception_reason_wizard_id',
		string="Revenue/Target Lines"
	)

	breadth_line_ids = fields.One2many(
		"commission.exception.wizard.breadth.line",
		'breadth_commission_structure_exception_reason_wizard_id',
		string="Breadth/Target Lines"
	)

	kpi_line_ids = fields.One2many(
		"commission.exception.wizard.kpi.line",
		'kpi_commission_structure_exception_reason_wizard_id',
		string="KPI/Target Lines"
	)

	ded_line_ids = fields.One2many(
		"commission.exception.wizard.ded.line",
		'kpi_commission_structure_exception_reason_wizard_id',
		string="Deduction Lines"
	)



	def action_confirm(self):
		active_id = self._context.get('active_id', False)
		active_model = self._context.get('active_model', False)
		commission_history = self.env[active_model].browse(active_id)

		for rec in self.revenue_line_ids:
			commissions_to_update = filter(lambda c: c.id == rec.line_id.id,
										   commission_history.commission_structure_line_ids)
			if rec.is_exception:
				for commission in commissions_to_update:
					commission.update({
						'is_exception': rec.is_exception,
						'exception_reason': rec.exception_reason,
						'exception_state': 'exception',
						'commission_to_be': rec.commission_to_be,
					})
			for commission in commissions_to_update:
				commission.update({
					'commission_to_be': rec.commission_to_be,
				})

		for rec in self.breadth_line_ids:
			breadth_line_update = filter(lambda c: c.id == rec.line_id.id,
										 commission_history.breadth_commission_structure_line_ids)
			if rec.is_exception:
				for commission in breadth_line_update:
					commission.update({
						'is_exception': rec.is_exception,
						'exception_reason': rec.exception_reason,
						'exception_state': 'exception',
						'commission_to_be': rec.commission_to_be,
					})

			for breadth_commission in breadth_line_update:
				breadth_commission.update({
					'commission_to_be': rec.commission_to_be,
				})

		for rec in self.kpi_line_ids:
			kpi_line_update = filter(lambda c: c.id == rec.line_id.id,
									 commission_history.kpi_commission_structure_line_ids)

			if rec.is_exception:
				for kpi_commission in kpi_line_update:
					kpi_commission.update({
						'is_exception': rec.is_exception,
						'exception_reason': rec.exception_reason,
						'exception_state': 'exception',
						'manager_result_to_be': rec.manager_result_to_be,
					})

			for kpi_commission in kpi_line_update:
				kpi_commission.update({
					'manager_result_to_be': rec.manager_result_to_be,
				})
		
		for rec in self.ded_line_ids:
			ded_line_update = filter(lambda c: c.id == rec.line_id.id,
									 commission_history.ded_commission_structure_line_ids)

			if rec.is_exception:
				for ded_commission in ded_line_update:
					ded_commission.update({
						'is_exception': rec.is_exception,
						'exception_reason': rec.exception_reason,
						'exception_state': 'exception',
						'manager_result_to_be': rec.manager_result_to_be,
					})

			for ded_commission in ded_line_update:
				ded_commission.update({
					'manager_result_to_be': rec.manager_result_to_be,
				})

		commission_history.update({
			'exception_state': 'exception',
		})
