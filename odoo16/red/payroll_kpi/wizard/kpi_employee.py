from odoo import _, api, fields, models
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class HrPayrollKPIEmployees(models.TransientModel):
	_name = 'kpi.employee.wizard'
	_description = 'Generate kpi for each month for all selected employees'

	employee_id = fields.Many2one('hr.employee', readonly=True)
	employee_kpi_id = fields.Many2one('employee.kpi', string='Employee KPI')
	payroll_kpi_ids = fields.Many2many('payroll.kpi', string='Employee KPIs', ondelete='cascade')

	


	def action_rate(self):
		for rec in self.payroll_kpi_ids:
			if not rec.manager_remarks and rec.kpi != rec.score:
				raise ValidationError(_(f"Please provide a remark for {rec.category_id.name}"))
			rec.write({
				'state': 'rated'
			})
		
		self.employee_kpi_id.write({
			'state': 'rated'
		})

		# return to current action
		return {'type': 'ir.actions.act_window_close'}

	def unlink(self):
		for rec in self.payroll_kpi_ids:
			rec.sudo().unlink()
		res = super(HrPayrollKPIEmployees, self).unlink()
		self.clear_caches()
		
		return res

	def _close(self, options):
		self.unlink()
		self.clear_caches()
		res = super(HrPayrollKPIEmployees, self)._close(options)	
		return res
		
	def action_cancel(self):
		self.unlink()
		return {'type': 'ir.actions.act_window_close'}

		





	

   