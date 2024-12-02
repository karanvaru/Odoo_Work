# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import datetime

class JobPositions(models.Model):
    _name = "job.positions"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Job Positions'

    name = fields.Char('Name', default=lambda self: _('New'),store=True,track_visibility='onchange')
    stage = fields.Selection([
        ('draft', 'Draft'),
        ('start', 'Start'),
        ('join', 'Joined'),
        ('cancel','Cancelled'),
    ], string='Status', default='draft', track_visibility='onchange')

    job_position = fields.Many2one('hr.job', string='Job Position', track_visibility='onchange')
    # department = fields.Many2one('hr.department', string='Department', related='job_position.department_id', readonly=True, track_visibility='onchange')
    bcg= fields.Selection([
        ('business_continuity', 'Business Continuity'),
        ('growth', 'Growth'),
    ], string='BCG', track_visibility='onchange')
    work_location = fields.Many2one('x_work_location', string='Work Location', track_visibility='onchange')
    work_office = fields.Selection([
        ('property1', 'Property 1'),
        ('hyd_o1', 'Hyderabad Office 1'),
        ('hyd_o2', 'Hyderabad Office 2'),
        ('hyd_o3', 'Hyderabad Office 3'),
    ], string='Work Office', track_visibility='onchange')
    dot_4x_ap = fields.Boolean('Dot4X/A+', track_visibility='onchange')
    dot_4x_rdp2x = fields.Boolean('Dot4X/RDP2X', track_visibility='onchange')
    department_manager = fields.Many2one('res.users', string='Department Manager', domain="[('is_int_user','=',True)]", track_visibility='onchange')
    department_hod = fields.Many2one('res.users', string='Department HOD', domain="[('is_int_user','=',True)]", track_visibility='onchange')
    recruiter = fields.Many2one('res.users', string='Recruiter', domain="[('is_int_user','=',True)]", track_visibility='onchange')
    hr_manager = fields.Many2one('res.users', string='HR Manager', domain="[('is_int_user','=',True)]", track_visibility='onchange')
    employee_category = fields.Many2one('hr.contract.type', 'Employee Category', track_visibility='onchange')
    payroll = fields.Selection([
        ('rdp','RDP'),
        ('third_party','Third Party'),
    ], string='Payroll', track_visibility='onchange')
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High'),
    ], string='Priority', track_visibility='onchange')
    jd_10_10_updated = fields.Integer('JD 10:10 Updated %', track_visibility='onchange',compute = 'action_get_jd_percentage', readonly=True)
    recruited_by = fields.Selection([
        ('rdp', 'RDP'),
        ('vendor', 'Vendor'),
        ('employee_referral','Employee Referral'),
    ], string='Recruited By', track_visibility='onchange')
    notes = fields.Text('Notes', track_visibility='onchange')
    vendors = fields.Many2many('res.partner', string='Vendors', track_visibility='onchange')
    # notice_period = fields.char('Notice Period', related='job_position.notice_period', readonly=True)
    # employment_bond = fields.char('Employment Bond', related='job_position.employment_bond', readonly=True)
    sta = fields.Many2many('rdp.sta', string='STA', track_visibility='onchange')
    salary_range = fields.Char('Salary Range', track_visibility='onchange')
    start_date = fields.Datetime('Start Date', track_visibility='onchange')
    join_date = fields.Datetime('Join Date',copy=False, track_visibility='onchange')
    # open_days = fields.Char('Open Days')
    # application_count = fields.Integer('Applications', related='job_position.application_count', readonly=True, track_visibility='onchange')
    # employee_count = fields.Integer('Employees', related='job_position.no_of_employee', readonly=True, track_visibility='onchange')
    application_count = fields.Integer('Applications', compute='compute_related', readonly=True)
    employee_count = fields.Integer('Employees', compute='compute_related', readonly=True)
    department = fields.Many2one('hr.department', string='Department', compute='compute_dept',
                                 readonly=True, track_visibility='onchange')
    @api.multi
    def _action_set_start_date(self):
        self.write({'state': 'refuse'})
        self.write({'start_date':datetime.datetime.now()})

    @api.multi
    def _action_set_join_date(self):
        self.write({'state': 'join'})
        self.write({'join_date': datetime.datetime.now()})

    @api.multi
    def _action_open_days(self):
        if not self.start_date and not self.join_date:
            self.open_days = 'Not Yet Started'
        if self.start_date and not self.join_date:
            self.open_days = (datetime.datetime.now() - self.start_date).split(',')[0]
        if self.start_date and self.join_date:
            self.open_days = (self.join_date - self.start_date).split(',')[0]

    @api.multi
    def action_get_jd_percentage(self):
        jd_p= self.job_position.x_studio_jd_1010_updated__1
        self.jd_10_10_updated = int(jd_p)

    @api.multi
    def action_cancel(self):
        self.write({'state','cancel'})


    @api.model
    def create(self,vals):
        vals.update({
			'name': self.env['ir.sequence'].next_by_code('job.position.sequence'),
		})
        return super(JobPositions, self).create(vals)

    # pavan changes

    @api.onchange('job_position')
    def compute_related(self):
        for rec in self:
            rec.application_count = rec.job_position.application_count
            rec.employee_count = rec.job_position.no_of_employee
            rec.department = rec.job_position.department_id

    @api.onchange('job_position')
    def compute_dept(self):
        for rec in self:
            # rec.application_count = rec.job_position.application_count
            # rec.employee_count = rec.job_position.no_of_employee
            rec.department = rec.job_position.department_id

class RdpSta(models.Model):
    _name = 'rdp.sta'

    name = fields.Char(required=True)


