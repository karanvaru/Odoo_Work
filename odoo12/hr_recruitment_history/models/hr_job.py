# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models
from odoo.tools.translate import _  
    
class Job(models.Model):
    _inherit = "hr.job"
    
    @api.multi
    def set_recruit(self):
        res = super(Job, self).set_recruit()
        for record in self:
            job_history = {
                'address_id': record.address_id.id,
                'alias_id': record.alias_id.id,
                'user_id': record.user_id.id,
                'company_id': record.company_id.id,
                'manager_id': record.manager_id.id,
                'department_id': record.department_id.id,
                'name': record.name,
                'requirements': record.requirements,
                'state': record.state,
                'description': record.description,
                'hr_responsible_id': record.hr_responsible_id.id,
                'display_name': record.display_name,
                'date_open': fields.Date.today(),
                'no_of_recruitment': record.no_of_recruitment,
                'no_of_employee': len(record.employee_ids.ids),
                'expected_employees': len(record.employee_ids.ids) + record.no_of_recruitment,          
                'job_id': record.id}
            self.env['hr.job.history'].create(job_history)
        return res

    @api.multi
    def set_open(self):
        result = dict.fromkeys(self.ids, self.env['ir.attachment'])        
        for record in self:
            job_history = self.env['hr.job.history'].search([('job_id', '=', record.id)], order='id DESC', limit=1)
            employee_ids = record.employee_ids.filtered(lambda self: not self.job_history_id)
            employee_ids.write({'job_history_id': job_history.id})
            application_ids = record.application_ids.filtered(lambda self: not self.job_history_id)
            application_ids.write({'job_history_id': job_history.id})
            applicants = application_ids.filtered(lambda self: not self.emp_id)
            app_to_job = dict((applicant.id, applicant.job_id.id) for applicant in applicants)
            attachments = self.env['ir.attachment'].search([
                '|',
                '&', ('res_model', '=', 'hr.job'), ('res_id', 'in', [record.id]),
                '&', ('res_model', '=', 'hr.applicant'), ('res_id', 'in', applicants.ids)])
            for attachment in attachments:
                if attachment.res_model == 'hr.applicant':
                    result[app_to_job[attachment.res_id]] |= attachment
                else:
                    result[attachment.res_id] |= attachment
            applicants_sources = self.env['hr.recruitment.source'].search([
                ('job_id', '=', record.id), ('job_history_id', '=', False)])
            applicants_sources.write({'job_history_id': job_history.id})                    
            job_history.write({
                'date_closed': fields.Date.today(), 
                'no_of_recruitment': record.no_of_recruitment,
                'no_of_hired_employee': record.no_of_hired_employee,
                'application_count': len(application_ids.ids),
                'expected_employees': job_history.no_of_employee + record.no_of_recruitment,
                'document_ids': result[record.id],
                'documents_count': len(result[record.id])
                })
        res = super(Job, self).set_open()
        return res

class JobHistory(models.Model):    
    _name = "hr.job.history"
    _description = "Job Position History"
    _order = 'id DESC'
    
    name = fields.Char(string='Job Position', index=True, translate=True, readonly=True)
    date_open = fields.Date('Open Date', readonly=True)
    date_closed = fields.Date("Closed Date", readonly=True)
    expected_employees = fields.Integer(string='Total Forecasted Employees', readonly=True, help='Expected number of employees for this job position after new recruitment.')
    no_of_employee = fields.Integer(string="Number of Employees", readonly=True, help='Number of employees occupying this job position.')
    no_of_recruitment = fields.Integer(string='Expected Employees', readonly=True, help='Number of new employees you expected to recruit.')
    no_of_hired_employee = fields.Integer(string='Hired Employees', readonly=True,
        help='Number of hired employees for this job position during recruitment phase.')
    employee_ids = fields.One2many('hr.employee', 'job_history_id', string='Employees', readonly=True, groups='base.group_user')
    description = fields.Text(string='Job Description', readonly=True)
    requirements = fields.Text('Requirements', readonly=True)
    department_id = fields.Many2one('hr.department', string='Department', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    state = fields.Selection([
        ('recruit', 'Recruitment in Progress'),
        ('open', 'Not Recruiting')
    ], string='Status', readonly=True, default='recruit', help="Set whether the recruitment process is open or closed for this job position.")
    address_id = fields.Many2one('res.partner', "Job Location", readonly=True, help="Address where employees are working")
    application_ids = fields.One2many('hr.applicant', 'job_history_id', "Applications", readonly=True)
    application_count = fields.Integer(string="Number of Applications", readonly=True)
    manager_id = fields.Many2one('hr.employee', string="Department Manager", readonly=True)
    user_id = fields.Many2one('res.users', "Recruitment Responsible", readonly=True)
    hr_responsible_id = fields.Many2one('res.users', "HR Responsible", readonly=True, help="Person responsible of validating the employee's contracts.")
    document_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'hr.job.history')], string='Documents', readonly=True)
    documents_count = fields.Integer(string="Document Count", readonly=True)
    alias_id = fields.Many2one(
        'mail.alias', "Alias", ondelete="restrict", readonly=True,
        help="Email alias for this job position. New emails will automatically create new applicants for this job position.")   
    job_id = fields.Many2one('hr.job', 'Job Position', readonly=True)
    
    @api.multi
    def action_get_attachment_tree_view(self):
        action = self.env.ref('base.action_attachment').read()[0]
        action['context'] = {
            'default_res_model': self._name,
            'default_res_id': self.ids[0],
            'create': False,
            'delete': False
        }
        action['search_view_id'] = (self.env.ref('hr_recruitment.ir_attachment_view_search_inherit_hr_recruitment').id, )
        action['domain'] = ['|', '&', ('res_model', '=', 'hr.job'), ('res_id', 'in', [self.job_id.id]), '&', ('res_model', '=', 'hr.applicant'), ('res_id', 'in', self.mapped('application_ids').ids)]
        return action    
            
class Employee(models.Model):
    _inherit = "hr.employee"
    
    job_history_id = fields.Many2one('hr.job.history', 'Job History')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    