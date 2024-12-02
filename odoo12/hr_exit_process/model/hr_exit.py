#!/usr/bin/python
# -*- coding: utf-8 -*-

import time

from openerp import models, fields, api, _
from openerp.exceptions import Warning
from datetime import datetime, timedelta, date


class hr_exit_checklist(models.Model):
    _name = 'hr.exit.checklist'

    name = fields.Char(string="Name", required=True)
    responsible_user_id = fields.Many2one('res.users', string='Responsible User', required=True)
    notes = fields.Text(string="Notes")
    checklist_line_ids = fields.One2many('hr.exit.checklist.line', 'checklist_line_id', string='Checklist')


class hr_exit_checklist_line(models.Model):
    _name = 'hr.exit.checklist.line'

    name = fields.Char(string="Name", required=True)
    checklist_line_id = fields.Many2one('hr.exit.checklist', invisible=True)


class hr_exit_line(models.Model):
    _name = 'hr.exit.line'
    _description = "Exit Lines"
    # _inherit = ['mail.thread', 'ir.needaction_mixin']
    _inherit = ['mail.thread', 'mail.activity.mixin']  # odoo11
    _rec_name = 'checklist_id'
    _order = 'id desc'

    checklist_id = fields.Many2one('hr.exit.checklist', string="Checklist", required=True)
    notes = fields.Text(string="Remarks")
    state = fields.Selection(selection=[('draft', 'New'), \
                                        ('confirm', 'Confirmed'), \
                                        ('approved', 'Approved'), \
                                        ('reject', 'Rejected'), \
                                        ('cancel', 'Cancelled')], \
                             string='State', default='draft', track_visibility='onchange')
    exit_id = fields.Many2one('hr.exit')
    responsible_user_id = fields.Many2one('res.users', string='Responsible User', required=True)
    user_id = fields.Many2one(related="exit_id.user_id", string="User", type='many2one', relation='res.users', \
                              readonly=True, store=True)
    checklist_line_ids = fields.Many2many('hr.exit.checklist.line',
                                          'rel_exit_checklist_line', 'exit_line_id', 'checklist_exit_line_id',
                                          string='Checklist Lines')

    @api.onchange('checklist_id')
    def get_checklistline(self):
        self.checklist_line_ids = self.checklist_id.checklist_line_ids

    @api.multi
    def checklist_confirm(self):
        self.state = 'confirm'

    @api.multi
    def checklist_approved(self):
        self.state = 'approved'

    @api.multi
    def checklist_cancel(self):
        self.state = 'cancel'

    @api.multi
    def checklist_reject(self):
        self.state = 'reject'


class hr_exit(models.Model):
    _name = 'hr.exit'
    _description = "Exit"
    _rec_name = 'create_uid'
    # _inherit = ['mail.thread', 'ir.needaction_mixin']
    _inherit = ['mail.thread', 'mail.activity.mixin']  # odoo11
    _order = 'id desc'

    employee_id = fields.Many2one('hr.employee', string="Employee", compute="compute_employee_name", store=True)
    request_date = fields.Datetime('Request Date', readonly='1', \
                                   default=fields.Datetime.now())
    user_id = fields.Many2one('res.users', string='User', \
                              default=lambda self: self.env.user, \
                              states={'draft': [('readonly', False)]}, readonly=True)
    confirm_date = fields.Date(string='Confirm Date(Employee)', \
                               readonly=True, copy=False)
    dept_approved_date = fields.Date(string='Approved Date(Department Manager)', \
                                     readonly=True, copy=False)
    validate_date = fields.Date(string='Approved Date(HR Manager)', \
                                readonly=True, copy=False)
    general_validate_date = fields.Date(string='Approved Date(General Manager)', \
                                        readonly=True, copy=False)

    confirm_by_id = fields.Many2one('res.users', string='Confirm By', readonly=True, copy=False)
    dept_manager_by_id = fields.Many2one('res.users', string='Approved By Department Manager', readonly=True,
                                         copy=False)
    hr_manager_by_id = fields.Many2one('res.users', string='Approved By HR Manager', readonly=True, copy=False)
    gen_man_by_id = fields.Many2one('res.users', string='Approved By General Manager', readonly=True, copy=False)
    reason_for_leaving = fields.Char(string='Reason For Leaving', required=True, copy=False, readonly=True)
    survey = fields.Many2one('survey.survey', string=" Exit Interview Form", readonly=True)
    response_id = fields.Many2one('survey.user_input', "Response", ondelete="set null", oldname="response")
    partner_id = fields.Many2one('res.partner', "Contact", readonly=True)

    state = fields.Selection(selection=[
        ('draft', 'Draft'), \
        ('confirm', 'Confirmed'), \
        ('approved_dept_manager', 'Approved by Dept Manager'), \
        ('approved_hr_manager', 'Approved by HR Manager'), \
        ('fnf_completed', 'FNF Completed '),
        ('abscond', 'Absconded'), \
        # ('approved_general_manager', 'Approved by General Manager'),\
        ('done', 'Done'), \
        ('cancel', 'Cancel'), \
        ('withdrawn', 'Withdrawn')], string='State', \
        readonly=True, help='', default='draft', \
        track_visibility='onchange')
    notes = fields.Text(string='Notes')
    manager_id = fields.Many2one('hr.employee', 'Department Manager', related='employee_id.parent_id', store=True)
    # manager_id = fields.Many2one('hr.employee', 'Department Manager', \
    #                     related='employee_id.department_id.manager_id', \
    #                     states={'draft':[('readonly', False)]}, readonly=True, store=True,\
    #                     help='This area is automatically filled by the user who \
    #                     will confirm the exit', copy=False)
    department_id = fields.Many2one(related='employee_id.department_id', \
                                    string='Department', type='many2one', relation='hr.department', \
                                    readonly=True, store=True)
    job_id = fields.Many2one(related='employee_id.job_id', \
                             string='Job Title', type='many2one', relation='hr.department', \
                             readonly=True, store=True)
    checklist_ids = fields.One2many('hr.exit.line', 'exit_id', string="Checklist")
    contract_id = fields.Many2one('hr.contract', string='Contract', readonly=False)
    contract_ids = fields.Many2many('hr.contract', 'hr_contract_contract_tag')
    upload_a_document = fields.Binary(string="Upload A Document")
    spoc_id = fields.Many2one("hr.employee", 'SPOC', related="employee_id.coach_id")
    notice_period = fields.Selection([
        ('one_month', '30 Days'),
        ('two_month', '60 Days'),
        ('three_month', '90 Days'),
    ], string='Notice Period', compute="compute_last_work_date")
    last_work_date = fields.Char(string="Last Day Work", compute="compute_last_work_date", store=True)
    employee_mail = fields.Char(string="Employee Mail", compute="compute_mail")
    current_user_mail = fields.Char(string="User Mail", compute="compute_mail")
    is_withdrawn_button_visible = fields.Boolean(string="Withdrawn button visible", compute="_compute_button_visibility")

    @api.depends('employee_id', 'create_uid')
    def compute_mail(self):
        current_user_mail = self.env.user.email
        print("_____pppppp_______",current_user_mail)
        for rec in self:
            rec.employee_mail = rec.employee_id.work_email
            print("_________sssss______",rec.employee_mail)
            rec.current_user_mail = current_user_mail
            print(("__________qqqqqqqqq_______", rec.current_user_mail))

    @api.depends('employee_mail', 'current_user_mail')
    def _compute_button_visibility(self):
        for rec in self:
            if rec.employee_mail == rec.current_user_mail:
                rec.is_withdrawn_button_visible = True
            else:
                rec.is_withdrawn_button_visible = False

    @api.depends('user_id')
    def compute_employee_name(self):
        for rec in self:
            employee = rec.env['hr.employee'].search([('user_id', '=', rec.env.uid)])
            rec.employee_id = employee.id

    @api.depends('employee_id', 'employee_id.notice_period')
    def compute_last_work_date(self):
        for rec in self:
            if rec.employee_id.notice_period:
                rec.notice_period = rec.employee_id.notice_period
                if rec.notice_period == 'one_month':
                    x_month = (rec.request_date + timedelta(days=30))
                    rec.last_work_date = x_month.date()
                elif rec.notice_period == 'two_month':
                    y_month = (rec.request_date + timedelta(days=60))
                    rec.last_work_date = y_month.date()
                elif rec.notice_period == 'three_month':
                    z_month = (rec.request_date + timedelta(days=90))
                    rec.last_work_date = z_month.date()
                else:
                    rec.last_work_date = ""

    @api.multi
    def action_makeMeeting(self):
        """ This opens Meeting's calendar view to schedule meeting on current applicant
            @return: Dictionary value for created Meeting view
        """
        #         self.ensure_one()
        #         partners = self.partner_id | self.user_id.partner_id | self.department_id.manager_id.user_id.partner_id

        #         category = self.env.ref('hr_recruitment.categ_meet_interview')
        res = self.env['ir.actions.act_window'].for_xml_id('calendar', 'action_calendar_event')
        #         res['context'] = {
        #             'search_default_partner_ids': self.partner_id.name,
        #             'default_partner_ids': partners.ids,
        #             'default_user_id': self.env.uid,
        #             'default_name': self.name,
        #             'default_categ_ids': category and [category.id] or False,
        #         }
        return res

    @api.multi
    def action_start_survey(self):
        self.ensure_one()
        # create a response and link it to this applicant
        if not self.response_id:
            response = self.env['survey.user_input'].create(
                {'survey_id': self.survey.id, 'partner_id': self.partner_id.id})
            self.response_id = response.id
        else:
            response = self.response_id
        # grab the token of the response and start surveying
        return self.survey.with_context(survey_token=response.token).action_start_survey()

    @api.multi
    def action_print_survey(self):
        """ If response is available then print this response otherwise print survey form (print template of the survey) """
        self.ensure_one()
        if not self.response_id:
            return self.survey.action_print_survey()
        else:
            response = self.response_id
            return self.survey.with_context(survey_token=response.token).action_print_survey()

    @api.one
    def get_contract_latest(self, employee, date_from, date_to):
        """
        @param employee: browse record of employee
        @param date_from: date field
        @param date_to: date field
        @return: returns the ids of all the contracts for the given employee that need to be considered for the given dates
        """
        contract_obj = self.env['hr.contract']
        clause = []
        # a contract is valid if it ends between the given dates
        clause_1 = ['&', ('date_end', '<=', date_to), ('date_end', '>=', date_from)]
        # OR if it starts between the given dates
        clause_2 = ['&', ('date_start', '<=', date_to), ('date_start', '>=', date_from)]
        # OR if it starts before the date_from and finish after the date_end (or never finish)
        clause_3 = ['&', ('date_start', '<=', date_from), '|', ('date_end', '=', False), ('date_end', '>=', date_to)]
        clause_final = [('employee_id', '=', employee.id), '|', '|'] + clause_1 + clause_2 + clause_3
        contract_ids = contract_obj.search(clause_final, limit=1)
        return contract_ids

    @api.onchange('employee_id', 'state')
    def get_contract(self):
        contract_obj = self.env['hr.contract']
        #        if not self.employee_id.address_home_id:
        #            raise Warning(_('The employee must have a home address.'))
        self.partner_id = self.employee_id.address_home_id.id
        all_contract_ids = contract_obj.search([('employee_id', '=', self.employee_id.id)])
        contract_ids = self.get_contract_latest(self.employee_id, self.request_date, self.request_date)
        if contract_ids:
            self.contract_id = contract_ids[0].id
            self.contract_ids = all_contract_ids.ids

    @api.multi
    def exit_approved_by_department(self):
        obj_emp = self.env['hr.employee']
        self.state = 'confirm'
        self.dept_approved_date = time.strftime('%Y-%m-%d')

    @api.multi
    def request_set(self):
        self.state = 'draft'

    @api.multi
    def action_abscond(self):
        self.state = 'abscond'

    @api.multi
    def exit_cancel(self):
        self.state = 'cancel'

    @api.multi
    def get_confirm(self):
        self.state = 'confirm'
        self.confirm_date = time.strftime('%Y-%m-%d')
        self.confirm_by_id = self.env.user.id
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        self.base_url = base_url

        template_id = self.env['ir.model.data'].get_object_reference('hr_exit_process',
                                                                     'hr_exit_create_manager_email_template')[1]
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, base_url)
        template_id = self.env['ir.model.data'].get_object_reference('hr_exit_process',
                                                                     'hr_employee_exit_created_email_template')[1]
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, base_url)

    @api.multi
    def get_apprv_dept_manager(self):
        self.state = 'approved_dept_manager'
        self.dept_approved_date = time.strftime('%Y-%m-%d')
        self.dept_manager_by_id = self.env.user.id
        checklist_data = self.env['hr.exit.checklist'].search([])
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        self.base_url = base_url
        for checklist in checklist_data:
            vals = {'checklist_id': checklist.id,
                    'exit_id': self.id,
                    'state': 'confirm',
                    'responsible_user_id': checklist.responsible_user_id.id,
                    'checklist_line_ids': [(6, 0, checklist.checklist_line_ids.ids)]}
            self.env['hr.exit.line'].create(vals)
        template_id = self.env['ir.model.data'].get_object_reference('hr_exit_process',
                                                                     'manager_approval_conformation_to_employee_email_template')[
            1]
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, base_url)
        template_id = self.env['ir.model.data'].get_object_reference('hr_exit_process',
                                                                     'manager_approval_conformation_to_hr_email_template')[
            1]
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, base_url)

    @api.multi
    def get_apprv_hr_manager(self):
        self.state = 'approved_hr_manager'
        self.validate_date = time.strftime('%Y-%m-%d')
        self.hr_manager_by_id = self.env.user.id
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        self.base_url = base_url
        template_id = self.env['ir.model.data'].get_object_reference('hr_exit_process',
                                                                     'hr_manager_approval_conformation_to_employee_email_template')[
            1]
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, base_url)
        template_id = self.env['ir.model.data'].get_object_reference('hr_exit_process',
                                                                     'hr_manager_approval_conformation_to_manager_email_template')[
            1]
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, base_url)
        # for record in self.checklist_ids:
        #     if not record.state in ['approved']:
        #         raise Warning(_('You can not approved this request since there are some checklist to be approved by respected department'))

    # @api.multi
    # def get_apprv_general_manager(self):
    #     self.state = 'approved_general_manager'
    #     self.general_validate_date = time.strftime('%Y-%m-%d')
    #     self.gen_man_by_id = self.env.user.id

    @api.multi
    def get_apprv_f_and_f(self):
        self.state = 'fnf_completed'
        self.general_validate_date = time.strftime('%Y-%m-%d')
        self.gen_man_by_id = self.env.user.id
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        self.base_url = base_url
        template_id = self.env['ir.model.data'].get_object_reference('hr_exit_process',
                                                                     'fnf_completed_conformation_to_employee_email_template')[
            1]
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, base_url)
        template_id = self.env['ir.model.data'].get_object_reference('hr_exit_process',
                                                                     'fnf_completed_conformation_to_manager_email_template')[
            1]
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, base_url)

    @api.multi
    def get_done(self):
        self.state = 'done'

    @api.multi
    def get_withdrawn(self):
        self.state = 'withdrawn'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
