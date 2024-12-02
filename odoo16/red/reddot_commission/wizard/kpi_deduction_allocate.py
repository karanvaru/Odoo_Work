from odoo import _, api, fields, models
import logging
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)





class DeductionCommissionAllocate(models.TransientModel):
	_name = 'deduction.commission.allocate'
	_description = 'Deduction Commission Allocate'

	commission_structure_id = fields.Many2one('commission.structure', 'Commission Structure')
	line_ids = fields.One2many('ded.commission.allocate.lines', 'ded_allocation_id', string='Deduction Lines')



	def action_submit(self):
		active_id = self._context.get('active_id', False)
		active_model = self._context.get('active_model', False)
		commission_history = self.env[active_model].browse(active_id)
		for line in self.line_ids:
			if not line.comment:
				raise ValidationError(_("It's Mandatory to Write a Comment!"))
			line.ded_line_id.update(

				{
					'manager_result': line.manager_result,
					'comment': line.comment

			})
		commission_history.action_validate_deduction()





class DedCommissionAllocateLines(models.TransientModel):
	_name = 'ded.commission.allocate.lines'
	_description = 'Deduction Commission Allocate Lines'


	ded_allocation_id = fields.Many2one('deduction.commission.allocate', 'Deduction Commission Allocate')
	ded_line_id = fields.Many2one('commission.structure.deduction.line', 'Deduction Line Item')
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


