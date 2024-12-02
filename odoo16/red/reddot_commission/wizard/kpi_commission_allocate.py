from odoo import _, api, fields, models
import logging
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)





class KpiCommissionAllocate(models.TransientModel):
	_name = 'kpi.commission.allocate'
	_description = 'Kpi Commission Allocate'

	commission_structure_id = fields.Many2one('commission.structure', 'Commission Structure')
	line_ids = fields.One2many('kpi.commission.allocate.lines', 'kpi_allocation_id', string='KPI Lines')



	def action_submit(self):
		active_id = self._context.get('active_id', False)
		active_model = self._context.get('active_model', False)
		commission_history = self.env[active_model].browse(active_id)
		for line in self.line_ids:
			if not line.comment:
				raise ValidationError(_("It's Mandatory to Write a Comment!"))
			line.kpi_line_id.update(

				{
					'manager_result': line.manager_result,
					'comment': line.comment

			})
		commission_history.action_validate_kpi()





class KpiCommissionAllocateLines(models.TransientModel):
	_name = 'kpi.commission.allocate.lines'
	_description = 'Kpi Commission Allocate Lines'


	kpi_allocation_id = fields.Many2one('kpi.commission.allocate', 'KPI Commission Allocate')
	kpi_line_id = fields.Many2one('commission.structure.kpi.line', 'KPI Line Item')
	manager_result = fields.Selection(
		selection=[
			('pass', 'Pass'),
			('fail', 'Fail'),
		],
		default="pass",
	)
	comment = fields.Text(
		string="Comment"
	)


