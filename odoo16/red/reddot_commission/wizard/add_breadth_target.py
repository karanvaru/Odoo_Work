from odoo import _, api, fields, models
import logging


_logger = logging.getLogger(__name__)






class EmployeeBreadthTargetWizard(models.Model):
	_name = 'employee.breadth.target.wizard'
	_description = 'Employee Breadth Target Wizard'


	commission_structure_id = fields.Many2one('commission.structure', 'Commission Structure')
	line_ids = fields.One2many('employee.breadth.target.wizard.line', 'allocation_id', string='Target Lines')
	breadth_target_id = fields.Many2one('employee.target', 'Target', domain="[('target_type', '=', 'breadth')]")


	def update_breadth_line(self, target, count):
		_logger.error(f"counts: {target.target_breadth_count}, {count}")
		if target.target_breadth_count != count:
			target.sudo().write({
				'target_breadth_count': count
			})

	
	def action_submit(self):
		for rec in self:
			for line in self.line_ids:
				target_type = "breadth"
				domain = [
					('parent_id', '=', rec.breadth_target_id.id),
					('user_id', '=', rec.commission_structure_id.user_id.id),
				]
				
				if line.business_unit_id:
					val = ('business_unit_id', '=', line.business_unit_id.id)
					domain.append(val)				
				if line.company_id:
					val = ('company_id', '=', line.company_id.id)
					domain.append(val)	
				if line.bu_group_id:
					val = ('bu_group_id', '=', line.bu_group_id.id)
					domain.append(val)	
				if line.country_id:
					val = ('country_id', '=', line.country_id.id)
					domain.append(val)	

				if line.country_group_id:
					val = ('country_group_id', '=', line.country_group_id.id)
					domain.append(val)
						

				target_line = self.env['employee.target.lines'].search(domain, limit=1)
				if target_line:
					self.update_breadth_line(target_line, line.count)
				else:
					usd = self.env.ref('base.USD')
					vals = {
						'target_breadth_count': line.count,
						'user_id': rec.commission_structure_id.user_id.id,
						'company_id': line.company_id.id,
						'business_unit_id': line.business_unit_id.id,
						'bu_group_id': line.bu_group_id.id,
						'country_id': line.country_id.id,
						'country_group_id': line.country_group_id.id,
						'parent_id': rec.breadth_target_id.id,
						'currency_id': usd.id
					}

					target_lines = self.env['employee.target.lines'].create(vals)
			rec.commission_structure_id._update_lines(target_type='breadth')
			

							

								
								
					





class EmployeeBreadthTargetWizardLine(models.Model):
	_name = 'employee.breadth.target.wizard.line'
	_description = 'Employee Breadth Target Wizard Line'

	allocation_id = fields.Many2one('employee.breadth.target.wizard', string='Allocation')
	count =  fields.Float('Breadth Count', default=0)
	
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

	
