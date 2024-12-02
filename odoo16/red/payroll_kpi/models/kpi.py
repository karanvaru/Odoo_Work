from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import logging
from datetime import datetime, date
import calendar
import datetime
from dateutil.relativedelta import relativedelta
import io
import base64
import xlsxwriter

_logger = logging.getLogger(__name__)



class KpiCategory(models.Model):
	_name = 'kpi.category'
	_description = 'Kpi Category'

	def _default_company_id(self):
		return self.env.user.company_id.id


	name = fields.Char('Name', required=True)
	company_id = fields.Many2one('res.company', string='company',
		default=_default_company_id)
	active = fields.Boolean(string='Active', default=True)


class KpiExceptions(models.Model):
	_name = 'kpi.exceptions'
	_description = 'KPI Exceptions'
	
	active = fields.Boolean('Active', default=True, readonly=False)

	name = fields.Char('Name', required=True, help='Name of the exception rule')
	excluded_department_ids = fields.Many2many(
		'hr.department', 
		string='Excluded Departments', 
		help='Departments to be excluded from KPI assignments'
	)
	excluded_job_position_ids = fields.Many2many(
		'hr.job', 
		string='Excluded Job Positions', 
		help='Job positions to be excluded from KPI assignments'
	)

	


class PayrollConfig(models.Model):
	_name = 'payroll.config'
	_description = 'Payroll Config'


	def _default_company_id(self):
		return self.env.user.company_id.id

	name = fields.Char('Name')
	category_id = fields.Many2one('kpi.category', 'Category',
						domain="[('active', '=', 'True')]")
	description = fields.Text('Description')
	score = fields.Integer('Score', required=True)
	department_ids = fields.Many2many('hr.department', string='Department')
	job_ids = fields.Many2many('hr.job', string='Job Position',
							domain="[('active', '=', 'True')]")
	company_id = fields.Many2one('res.company', string='company',
		default=_default_company_id)
	active = fields.Boolean(string='Active', default=True)


	# #raise validation error if department and job score exceeds more than 10
	# @api.onchange('score', 'department_id', 'job_ids')
	# def onchange_score_id(self):
	# 	for rec in self:
	# 		count = rec.score
	# 		if rec.department_ids:
	# 			for_all_departments = self.env['payroll.config'].search([
	# 				('department_ids', 'in', rec.department_ids.ids)
	# 			])
	# 			for_all_departments_score = sum([x.score for x in for_all_departments])
	# 			if (count + for_all_departments_score) > 10:
	# 				raise ValidationError("One of the Departments Exceeds the scores of 10")
				
	# 		if rec.job_ids:
	# 			for_all_jobs = self.env['payroll.config'].search([
	# 				('job_ids', '=', rec.job_ids.ids)
	# 			])	
	# 			for_all_jobs_score = sum([x.score for x in for_all_jobs])
	# 			if (count + for_all_jobs_score) > 10:
	# 				raise ValidationError("One of the Jobs Exceeds the scores of 10")



			

			

	


class EmployeeScore(models.Model):
	_name = 'employee.score'
	_description = 'Employee Score'
	_inherit = ["mail.thread", 'mail.activity.mixin', 'portal.mixin']
	_order = "id desc"

	# _sql_constraints = [
	# 	('name_uniq', 'unique (name)', 'You cannot have multiple records for the same department and same month.'),
	# ]

	def _get_default_date(self):
		return fields.Date.from_string(fields.Date.today())

	def get_current_employee(self):
		# Get the current user
		current_user = self.env.user

		# Check if the user is an employee
		if current_user and current_user.employee_ids:
			# Assuming that an employee can have multiple employee records, so we'll take the first one
			current_employee = current_user.employee_ids[0]
			return current_employee
		else:
			return None

	name = fields.Char('Name', compute='_compute_name', store=True, readonly=True)
	department_id = fields.Many2one('hr.department', string='department', readonly=True)
	kpi_ids = fields.One2many('employee.kpi', 'employee_score_id', string='Kpis', readonly=True)
	employee_id = fields.Many2one('hr.employee', string='Employee')
	active = fields.Boolean(string='Active', default=True)
	month = fields.Date('Month', default=_get_default_date)
	state = fields.Selection([
		('draft', 'Draft'),
		('to_rate', 'To Rate'),
		('rated', 'Rated'),
		('expired', 'Expired')
	], string='state', default='draft')

	def _default_company_id(self):
		return self.env.user.company_ids.ids

	company_id = fields.Many2many('res.company', string='company', required=True,
		default=_default_company_id)
	kpi_url = fields.Char('URL', compute='get_kpi_url', store=True)


	@api.depends('employee_id')
	def get_kpi_url(self):
		for kpi in self:
			ir_param = self.env['ir.config_parameter'].sudo()
			base_url = ir_param.get_param('web.base.url')
			action_id = self.env.ref('payroll_kpi.employee_score_action').id
			menu_id = self.env.ref('payroll_kpi.employee_score_menu').id
			company_id = kpi.employee_id.user_id.company_ids.ids
			companies="%2C".join(str(company) for company in company_id)
			if base_url:
				base_url += '/web#id=%s&action=%s&model=%s&view_type=form&cids=%s&menu_id=%s' % (
				kpi.id, action_id, 'employee.score', companies, menu_id)
			kpi.kpi_url = base_url

	@api.model
	def default_get(self, fields):
		defaults = super(EmployeeScore, self).default_get(fields)
		defaults = self.action_generate(defaults)
		return defaults

	@api.model
	def create(self, vals):
		res = super().create(vals)
		for rec in res:
			rec.kpi_ids.write({
					'employee_score_id': rec.id
				})
		return res

	@api.depends('active', 'month', 'department_id')
	def _compute_name(self):
		for rec in self:

			employee = rec.get_current_employee()
			date = rec.month
			month = date.month - 1
			year = date.year

			if rec.employee_id:
				employee = rec.employee_id.name
			elif employee:
				employee = employee.name
			else:
				raise ValidationError(_("You do not have an Employee attached to your User. Contact IT"))
			name = f"{calendar.month_name[month]}-{year}, {employee}"
			if not rec.active:
					name += '-archived'
			
			count = self.env['employee.score'].search_count([
				('name', '=', name)
			])
			if count:
				name += f" {count}"
				count += 1
			rec.name = name
			

	def unlink(self):
		for rec in self:
			for kpi in rec.kpi_ids:
				kpi.employee_id.payroll_kpi_ids.filtered(lambda l: l.month == self.month).unlink()
		res = super(EmployeeScore, self).unlink()
		return res

	def autogenerate_records(self):
		employees = self.env['hr.employee'].sudo().search([('active', '=', True)])
		scores = []
		exceptions = self.env['kpi.exceptions'].search([
			('active', '=', True)
		])
		departments = []
		positions = []

		for exception in exceptions:
			for department in exception.excluded_department_ids:
				if department.id not in departments: 
					departments.append(department.id)
			
			for position in exception.excluded_job_position_ids:
				if position.id not in positions:
					positions.append(position.id)

		for employee in employees:	
			if employee.child_ids:
				employees = employee.child_ids
				_dict = []
				for emp in employees:
# 					if emp.state == 'payroll_employee':
# 						continue
					
					if emp.job_id.id in positions or emp.department_id.id in departments:
						continue
					emp_dict = {
						'employee_id': emp.id,
						'employee_score_id': self.id                    
					}
					_dict.append(emp_dict)
				if _dict:
					kpis = self.env['employee.kpi'].create(_dict)
					vals = {
						'kpi_ids': kpis,
						'month': datetime.date.today(),
						'department_id': employee.department_id.id,
						'company_id': employee.user_id.company_ids,
						'employee_id': employee.id,
						'state': 'to_rate'
					}
					scores.append(vals)
		
		if scores:
			emp_score = self.env['employee.score'].create(scores)
			email_template = self.env.ref('payroll_kpi.send_email_to_manager_template')
			for score in emp_score:
				email_template.send_mail(score.id, force_send=True)


	def action_state_expired(self):
		for rec in self:
			for kpi in rec.kpi_ids:
				kpi.write({
					'state': 'expired'
				})
				payroll_kpis = self.env['payroll.kpi'].search([
						('employee_id', '=', kpi.employee_id.id),
						('month','=', rec.month),
						('state', '=', 'to_rate')
					])
				payroll_kpis.write({
					'state': 'expired'
				})
			rec.state = 'expired'
			email_template = self.env.ref('payroll_kpi.send_expired_score_template')
			email_template.send_mail(rec.employee_id.user_id.partner_id.id, force_send=True)

	def rate_all(self):
		for rec in self:
			for kpi in rec.kpi_ids.filtered(lambda m: m.state == 'to_rate'):
				employee = kpi.employee_id
				kpis = self.env['payroll.config'].search([
					'|',
					('department_ids', 'in', employee.department_id.id), 
					('department_ids', '=', False),
					'|',
					('job_ids', 'in', employee.job_id.id), 
					('job_ids', '=', False)
				])

				vals = []
				payroll_kpis = self.env['payroll.kpi'].search([
					('employee_id', '=', employee.id),
					('month','=', rec.month)
				])
				emp_kpis = []
				if payroll_kpis:
					emp_kpis = payroll_kpis
				else:
					for rec_kpi in kpis:
						_dict = {
							'month': rec.month,
							'employee_id': employee.id,
							'score': rec_kpi.score,
							'kpi_type_id': rec_kpi.id,
							'employee_kpi_id': kpi.id,
							'employee_score_id': rec.id,
							'company_id': employee.company_id.id
						}
						vals.append(_dict)
					emp_kpis = self.env['payroll.kpi'].sudo().create(vals)
				
				for pay_kpi in emp_kpis.filtered(lambda x: x.state == 'to_rate'):
					pay_kpi.write({
						'kpi' : pay_kpi.score,
						'state': 'rated'
					})
				kpi.write({
					'state': 'rated'
				})
			rec.write({
				'state': 'rated'
			})
				

	def action_reset_draft(self):
		for rec in self:
			for kpi in rec.kpi_ids:
				kpi.write({
					'state': 'to_rate'
				})
				payroll_kpis = self.env['payroll.kpi'].search([
						('employee_id', '=', kpi.employee_id.id),
						('month','=', rec.month)
					])
				payroll_kpis.write({
					'state': 'to_rate'
				})
			rec.state = 'draft'



	def action_generate(self, vals):
		employee = self.get_current_employee()
		if employee:
			if employee.child_ids:
				employees = employee.child_ids
				_dict = []
				for emp in employees:

					emp_dict = {
						'employee_id': emp.id,
						'employee_score_id': self.ids                      
					}
					_dict.append(emp_dict)
				vals['kpi_ids'] = self.env['employee.kpi'].create(_dict)
				vals['department_id'] = employee.department_id.id
				return vals
		return vals
				
			


	# remove button to remove from kpi_ids
	def action_remove(self):
		for rec in self:
			rec.kpi_ids.unlink()

	
	@api.depends('kpi_ids.state')
	def check_all_kpis_rated(self):
		for record in self:
			if record.kpi_ids and all(kpi.state == 'rated' for kpi in record.kpi_ids):
				record.state = 'rated'
					




class EmployeeKpi(models.Model):
	_name = 'employee.kpi'
	_description = 'Employee Kpi'

	employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
	employee_kpi_ids = fields.One2many('payroll.kpi', 'employee_kpi_id', string='Employee KPIs')
	state = fields.Selection(string='Status', selection=[('to_rate', 'To Rate'), ('rated', 'Rated'),('cancel', 'Cancel')], default='to_rate', readonly=True)
	employee_score_id = fields.Many2one('employee.score', string='Employee Score')
	month = fields.Date('Month', related='employee_score_id.month')


	def write(self, vals):
		result = super(EmployeeKpi, self).write(vals)
		if 'state' in vals and vals['state'] == 'rated':
			# Check and update the state of related employee score
			for kpi in self:
				if kpi.employee_score_id:
					kpi.employee_score_id.check_all_kpis_rated()
		return result
	

	def action_cancel(self):
		for rec in self:
			rec.employee_kpi_ids.unlink()
			rec.state = 'cancel'

	def _get_default_date(self):
		return fields.Date.from_string(fields.Date.today())

	#  button to generate kpis for employees defined
	def action_generate(self):
		for rec in self:
			employee = rec.employee_id
			kpis = self.env['payroll.config'].search([
				'|',
				('department_ids', 'in', employee.department_id.id), 
				('department_ids', '=', False),
				'|',
				 ('job_ids', 'in', employee.job_id.id), 
				 ('job_ids', '=', False)

			])

			vals = []
			payroll_kpis = self.env['payroll.kpi'].search([
				('employee_id', '=', employee.id),
				('month','=', rec.month)
			])
			if payroll_kpis:
				emp_kpis = payroll_kpis
			else:
				for kpi in kpis:
					_dict = {
						'month': rec.month,
						'employee_id': employee.id,
						'score': kpi.score,
						'kpi_type_id': kpi.id,
						'employee_kpi_id': rec.id,
						'employee_score_id': rec.employee_score_id.id,
					}
					vals.append(_dict)
				emp_kpis = self.env['payroll.kpi'].sudo().create(vals)
			
			# return action for wizard pop up
			
			wizard = self.env['kpi.employee.wizard'].create({
				'employee_id': employee.id,
				'employee_kpi_id': rec.id,
				'payroll_kpi_ids': emp_kpis.ids
			})
			return {
			'name': f'KPI for {employee.name}',
			'type': 'ir.actions.act_window',
			'res_model': 'kpi.employee.wizard',
			'view_mode': 'form',
			'target': 'new',
			'res_id': wizard.id,
			}




class PayrollKpi(models.Model):
	_name = 'payroll.kpi'
	_description = 'Payroll KPI'

	def _default_company_id(self):
		return self.env.user.company_id.id

	def _get_default_date(self):
		return fields.Date.from_string(fields.Date.today())


	month = fields.Date('month', default=_get_default_date)
	employee_id = fields.Many2one('hr.employee', string='employee', readonly=True)
	kpi = fields.Integer('KPI Achieved Score', default=0, required=True)
	department_id = fields.Many2one('hr.department', related='employee_id.department_id')
	job_id = fields.Many2one('hr.job', string='Job Position', related='employee_id.job_id')
	kpi_type_id = fields.Many2one('payroll.config', string='KPI Type', readonly=True)
	company_id = fields.Many2one('res.company', string='Company',
		default=_default_company_id)
	employee_score_id = fields.Many2one('employee.score', string='Employee Score')
	state = fields.Selection(string='Status', selection=[('to_rate', 'To Rate'), ('rated', 'Rated'),('cancel', 'Cancel')], default='to_rate')
	manager_remarks = fields.Char('Manager Remarks')
	score = fields.Integer(string="Score", related='kpi_type_id.score')
	category_id = fields.Many2one('kpi.category', 'Category', related='kpi_type_id.category_id')
	description = fields.Text('Description', related='kpi_type_id.description')
	employee_kpi_id = fields.Many2one('employee.kpi')

	



	@api.model
	def generate_and_send_kpi_report(self, recipient_email=None):
		# Get the current month and year
		today = date.today()
		start_of_month = today.replace(day=1)
		end_of_month = start_of_month + relativedelta(months=1, days=-1)

		# Query to get KPI records where the achieved score is less than the allocated score
		# and the date is within the current month
		kpi_records = self.search([
			('month', '>=', start_of_month),
			('month', '<=', end_of_month)
		]).filtered(lambda m: m.kpi < m.score)

		# Create an in-memory Excel workbook using xlsxwriter
		output = io.BytesIO()
		workbook = xlsxwriter.Workbook(output, {'in_memory': True})
		worksheet = workbook.add_worksheet('KPI Report')

		# Write headers
		headers = ['Employee Name', 'Company', 'Manager', 'KPI Name', 'Category', 'Allocated Score', 'Achieved Score', 'Remarks']
		for col_num, header in enumerate(headers):
			worksheet.write(0, col_num, header)

		# Write data rows
		for row_num, kpi in enumerate(kpi_records, start=1):
			worksheet.write(row_num, 0, kpi.employee_id.name or '')
			worksheet.write(row_num, 1, kpi.employee_id.company_id.name or '')
			worksheet.write(row_num, 2, kpi.employee_id.parent_id.name or '')
			worksheet.write(row_num, 3, kpi.description or '')
			worksheet.write(row_num, 4, kpi.category_id.name or '')
			worksheet.write(row_num, 5, kpi.score)
			worksheet.write(row_num, 6, kpi.kpi)
			worksheet.write(row_num, 7, kpi.manager_remarks or '')

		# Close the workbook
		workbook.close()
		output.seek(0)

		# Prepare the attachment
		attachment_data = base64.b64encode(output.read())

		# Define recipient email; if not provided, use a default (adjust as needed)
		if not recipient_email:
			recipient_email = self.env['ir.config_parameter'].sudo().get_param('hr_kpi_report.recipient_email', 'hr@reddotdistribution.com')

		# Send email with the attachment
		mail_values = {
			'subject': 'KPI Report for Current Month: Employees with KPI Ratings Below Allocated Marks',
			'body_html': '<p>Please find attached the KPI report for employees with achieved scores less than allocated marks for the current month.</p>',
			'email_to': recipient_email,
			'attachment_ids': [(0, 0, {
				'name': f'KPI_Report_{today.strftime("%Y_%m")}.xlsx',
				'datas': attachment_data,
				'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
			})]
		}
		self.env['mail.mail'].create(mail_values).send()

		return True
	
	

	


	@api.constrains('kpi', 'score')
	def _check_kpi_score(self):
		for record in self:
			if record.kpi > record.score or record.kpi < 0:
				raise ValidationError(f"KPI {record.category_id.name} should be between 0 and {record.score}")

	

	


class HrEmployee(models.Model):
	_inherit = 'hr.employee'


	payroll_kpi_ids = fields.One2many('payroll.kpi', 'employee_id', string='Payroll Kpi') 


	# function used in payroll rule to get all scores per employee
	def kpi_rate(self, date_from):
		relevant_kpis = [kpi.kpi for kpi in self.payroll_kpi_ids if date_from.month == kpi.month.month and kpi.state == 'rated' and self.employee_id.id == kpi.employee_id.id]  
		if not relevant_kpis:
			return 0   
		return sum(relevant_kpis)