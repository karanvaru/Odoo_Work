# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, date


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_ceo = fields.Boolean(string='Is CEO')

    @api.constrains('is_ceo')
    def _valid_team(self):
        if self.is_ceo:
            ceo_true = self.search([('id', '!=', self.id), ('is_ceo', '=', True)])
            if ceo_true:
                raise UserError(_('CEO role cannot be duplicated and exists already. Kindly update.'))

class Disciplinary(models.Model):
    _name = "employee.disciplinary"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee Disciplinary'

    name = fields.Char(string='Offense', required=True)
    message_ids = fields.One2many('mail.message', 'res_id', string='Messages', domain=[('model', '=', _name)])
    issuer = fields.Many2one('hr.employee', string='Issuer', required=True)
    type = fields.Many2one('disciplinary.type', string='Type')
    description = fields.Text(string='Description', required=True)
    employee = fields.Many2one('hr.employee', string='Employee', required=True)
    date = fields.Date(string='Date', default=fields.Date.today)
    open_days = fields.Char(compute='_compute_open_days',string='Open Days')
    employee_department = fields.Many2one('hr.department', string='Department', related='employee.department_id', readonly=True)
    issuer_department = fields.Many2one('hr.department', string='Department', related='issuer.department_id', readonly=True)
    company_id = fields.Many2one('res.company', string="Company")
    state = fields.Selection([
        ('submit', 'To Submit'),
        ('confirmed', 'Confirmed'),
        ('noticed', 'Noticed'),
        ('resolve', 'Resolved')], string='Status', default='submit', track_visibility='onchange')
    severity = fields.Many2one('disciplinary.severity', required=True)
    appeal_count = fields.Integer('Number of appeals', compute='_compute_appeal_count')
    pip_count = fields.Integer('Number of pip', compute='_compute_pip_count')
    resolve_date = fields.Datetime(string="Resolve Date", compute="_compute_resolve_date")
    delay_days = fields.Char(string="Delay Days", compute="compute_delay_days")
    spoc_id = fields.Many2one('hr.employee', string="HR SPOC", compute="compute_spoc")

    @api.depends('message_ids.write_date')
    def _compute_resolve_date(self):
        for record in self:
            messages = record.message_ids.sorted(key=lambda r: r.write_date, reverse=True)
            if messages:
                record.resolve_date = messages[0].write_date

    @api.depends('resolve_date')
    def compute_delay_days(self):
        for rec in self:
            if rec.state == 'resolve':
                rec.delay_days = str((rec.resolve_date - rec.create_date).days) + " Days"
            else:
                rec.delay_days = str((datetime.today() - rec.create_date).days) + " Days"

    @api.depends('employee')
    def compute_spoc(self):
        for rec in self:
            rec.spoc_id = rec.employee.coach_id

    @api.multi
    def button_confirmed(self):
        self.write({'state': 'confirmed'})
        self.activity_update()
        # self.resolve_date = datetime.today()

    @api.multi
    def button_approve(self):
        self.write({'state': 'noticed'})
        self.approve_update()
        self.approve1_update()
        # self.resolve_date = datetime.today()

    @api.multi
    def button_resolve(self):
        self.write({'state': 'resolve'})
        self.resolve_update()

    @api.multi
    def button_resolve2(self):
        self.write({'state': 'resolve'})
        self.resolve_update2()
        # self.resolve_date = datetime.today()

    @api.multi
    def _compute_pip_count(self):
        pips = self.env['employee.pip'].search_count([
            ('disciplinary', '=', self.id)
        ])
        self.pip_count = pips

    @api.multi
    def _compute_appeal_count(self):
        pips = self.env['employee.appeal'].search_count([
            ('disciplinary', '=', self.id)
        ])
        self.appeal_count = pips

    @api.multi
    def button_pip(self):
        return {
            'name': _('Pip Form'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'employee.pip',
            'type': 'ir.actions.act_window',
            'context': {
                'default_disciplinary': self.id,
            }
        }

    @api.multi
    def button_appeal(self):
        return {
            'name': _('Appeal Form'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'employee.appeal',
            'type': 'ir.actions.act_window',
            'context': {
                'default_disciplinary': self.id,
            }
        }

    @api.multi
    def button_grievance(self):
        return {
            'name': _('Grievance Form'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'employee.grievance',
            'type': 'ir.actions.act_window',
            'context': {
                'default_disciplinary': self.id,
            }
        }

    @api.model
    def default_get(self, fields):
        res = super(Disciplinary, self).default_get(fields)
        issuer = self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1)
        res.update({
            'issuer': issuer and issuer.id or False,
            })
        return res

    @api.multi
    def _get_responsible_for_confirm(self):
        if self.employee.parent_id:
            return self.employee.parent_id.user_id
        return self.env.user

    def activity_update(self):
        self.ensure_one()
        for expense_report in self.filtered(lambda hol: hol.state == 'confirmed'):
            self.activity_schedule(
                'disciplinary.mail_act_employee_disc',
                user_id=expense_report.sudo()._get_responsible_for_confirm().id)

    def _get_responsible_for_approve(self):
        if self.employee.coach_id:
            return self.employee.coach_id.user_id
        return self.env.user

    def approve_update(self):
        for expense_report in self.filtered(lambda hol: hol.state == 'noticed'):
            self.activity_schedule(
                'disciplinary.mail_act_employee_disc2',
                user_id=expense_report.sudo()._get_responsible_for_approve().id)
        self.filtered(lambda hol: hol.state == 'noticed').activity_unlink(['disciplinary.mail_act_employee_disc'])

    def _get_responsible_for_approve1(self):
        if self.employee:
            return self.employee.user_id
        return self.env.user

    def approve1_update(self):
        for expense_report in self.filtered(lambda hol: hol.state == 'noticed'):
            self.activity_schedule(
                'disciplinary.mail_act_employee_disc',
                user_id=expense_report.sudo()._get_responsible_for_approve1().id)

    def _get_responsible_for_resolve(self):
        if self.employee.coach_id:
            return self.employee.coach_id.user_id
        return self.env.user

    def resolve_update(self):
        for expense_report in self.filtered(lambda hol: hol.state == 'resolve'):
            self.activity_schedule(
                'disciplinary.mail_act_employee_disc',
                user_id=expense_report.sudo()._get_responsible_for_resolve().id)
        self.filtered(lambda hol: hol.state == 'resolve').activity_unlink(['disciplinary.mail_act_employee_disc'])
        self.filtered(lambda hol: hol.state == 'resolve').activity_unlink(['disciplinary.mail_act_employee_disc2'])

    def _get_responsible_for_resolve2(self):
        user_ids = self.env['res.users'].search([('groups_id', 'in', self.env.ref('disciplinary.group_manager').id)])
        return user_ids
        if self.employee.parent_id:
            return self.employee.parent_id.user_id
        return self.env.user

    def resolve_update2(self):
        for expense_report in self.filtered(lambda hol: hol.state == 'resolve'):
            self.activity_schedule(
                'disciplinary.mail_act_employee_disc3',
                user_id=expense_report.sudo()._get_responsible_for_resolve().id)
        self.filtered(lambda hol: hol.state == 'resolve').activity_unlink(['disciplinary.mail_act_employee_disc'])


    @api.depends('create_date')
    def _compute_open_days(self):
        for rec in self:
            if rec.create_date:
                if not rec.state == 'closed':
                    print("The create_date date is", rec.create_date)
                    print("The date of today", datetime.today())
                    today = datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S")
                    date = datetime.strptime(today, "%Y-%m-%d %H:%M:%S")
                    rec.open_days = str((date - rec.create_date).days + 1) + "  Days"

class DisciplinaryType(models.Model):
    _name = 'disciplinary.type'

    name = fields.Char(required=True)

class DisciplinarySeverity(models.Model):
    _name = 'disciplinary.severity'

    name = fields.Char(required=True)


class PIP(models.Model):
    _name = "employee.pip"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee PIP'

    _rec_name = 'employee_pip'
    supervisor = fields.Many2one('hr.employee', string='Supervisor', required=True)
    types = fields.Many2one(string='Type')
    description = fields.Text(string='Description')
    disciplinary = fields.Many2one('employee.disciplinary', string='Disciplinary')
    name = fields.Text(string='Name')
    employee_pip = fields.Many2one('hr.employee', string='Employee', required=True)
    severity = fields.Many2one(string='Severity')
    start_date = fields.Date(string='Start Date', default=fields.Date.today)
    end_date = fields.Date(string='End Date', required=True)
    review_date = fields.Date(string='Review Date', required=True)
    improvement = fields.Text(string='Steps for improvement', required=True)
    result = fields.Text(string='Required Results', required=True)
    state = fields.Selection([('submit', 'To Submit'), ('confirmed', 'Confirmed'), ('accept', 'Accepted'), ('resolve', 'Resolve'), ('refuse', 'Refused')], default='submit', track_visibility='onchange', string='Status')

    @api.multi
    def button_confirmed(self):
        self.write({'state': 'confirmed'})
        self.confirmed_update()

    @api.multi
    def button_accept(self):
        self.write({'state': 'accept'})
        self.accept_update()
        self.accept_update1()

    @api.multi
    def button_resolve(self):
        self.write({'state': 'resolve'})
        self.resolve_update()

    @api.multi
    def button_refuse(self):
        self.write({'state': 'refuse'})
        self.refuse_update()

    def _get_responsible_for_refuse(self):
        if self.employee_pip.coach_id:
            return self.employee_pip.coach_id.user_id
        return self.env.user

    def refuse_update(self):
        for expense_report in self.filtered(lambda hol: hol.state == 'refuse'):
            self.activity_schedule(
                'disciplinary.mail_act_employee_pip1',
                user_id=expense_report.sudo()._get_responsible_for_refuse().id)
        self.filtered(lambda hol: hol.state == 'refuse').activity_unlink(['disciplinary.mail_act_employee_pip'])

    @api.model
    def default_get(self, fields):
        res = super(PIP, self).default_get(fields)
        supervisor = self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1)
        res.update({
            'supervisor': supervisor and supervisor.id or False,
            })
        return res

    @api.multi
    def _get_responsible_for_confirm(self):
        if self.employee_pip:
            return self.employee_pip.user_id
        return self.env.user

    def confirmed_update(self):
        for expense_report in self.filtered(lambda hol: hol.state == 'confirmed'):
            self.activity_schedule(
                'disciplinary.mail_act_employee_pip',
                user_id=expense_report.sudo()._get_responsible_for_confirm().id)

    def _get_responsible_for_accept(self):
        if self.employee_pip.coach_id:
            return self.employee_pip.coach_id.user_id
        return self.env.user

    def accept_update(self):
        for expense_report in self.filtered(lambda hol: hol.state == 'accept'):
            self.activity_schedule(
                'disciplinary.mail_act_employee_pip3',
                user_id=expense_report.sudo()._get_responsible_for_accept().id)
        self.filtered(lambda hol: hol.state == 'accept').activity_unlink(['disciplinary.mail_act_employee_pip'])

    def resolve_update(self):
        self.filtered(lambda hol: hol.state == 'resolve').activity_unlink(['disciplinary.mail_act_employee_pip3'])

    def _get_responsible_for_accept1(self):
        if self.employee_pip.parent_id:
            return self.employee_pip.parent_id.user_id
        return self.env.user

    def accept_update1(self):
        for expense_report in self.filtered(lambda hol: hol.state == 'accept'):
            self.activity_schedule(
                'disciplinary.mail_act_employee_pip3',
                user_id=expense_report.sudo()._get_responsible_for_accept1().id)

class Appeal(models.Model):
    _name = "employee.appeal"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee Appeal'

    def _default_employee_appeal(self):
        return self.env.context.get('_default_employee_appeal') or self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)

    _rec_name = 'employee'
    description = fields.Text(string='Description', required=True)
    disciplinary = fields.Many2one('employee.disciplinary', string='Disciplinary')
    name = fields.Text(string='Name')
    employee = fields.Many2one('hr.employee', string='Employee', required=True, default=_default_employee_appeal)
    state = fields.Selection([('submit', 'To Submit'), ('confirmed', 'Confirmed'), ('accept', 'Accepted'), ('upheld', 'Upheld'), ('refuse', 'Refused')], default='submit', track_visibility='onchange')

    @api.multi
    def button_confirmed(self):
        self.write({'state': 'confirmed'})
        self.confirmed_update()

    @api.multi
    def button_accept(self):
        self.write({'state': 'accept'})
        self.accept_update()
        self.accept_update1()

    @api.multi
    def button_upheld(self):
        self.write({'state': 'upheld'})
        self.upheld_update()
        self.upheld1_update()

    @api.multi
    def button_refuse(self):
        self.write({'state': 'refuse'})
        self.refuse_update()
        self.refuse_update2()

    @api.multi
    def _get_responsible_for_refuse2(self):
        if self.employee.parent_id:
            return self.employee.parent_id.user_id
        return self.env.user

    def refuse_update2(self):
        for expense_report in self.filtered(lambda hol: hol.state == 'refuse'):
            self.activity_schedule(
                'disciplinary.mail_act_employee_disc4',
                user_id=expense_report.sudo()._get_responsible_for_refuse2().id)
            self.filtered(lambda hol: hol.state == 'accept').activity_unlink(['disciplinary.mail_act_employee_appeal'])

    @api.multi
    def _get_responsible_for_confirm(self):
        if self.employee.parent_id:
            return self.employee.parent_id.user_id
        return self.env.user

    def confirmed_update(self):
        for expense_report in self.filtered(lambda hol: hol.state == 'confirmed'):
            self.activity_schedule(
                'disciplinary.mail_act_employee_appeal',
                user_id=expense_report.sudo()._get_responsible_for_confirm().id)

    def _get_responsible_for_accept(self):
        user_ids = self.env['hr.employee'].search([('is_ceo', '=', True)])
        if user_ids:
            return user_ids.user_id

    def accept_update(self):
        for expense_report in self.filtered(lambda hol: hol.state == 'accept'):
            self.activity_schedule(
                'disciplinary.mail_act_employee_appeal1',
                user_id=expense_report.sudo()._get_responsible_for_accept().id)
        self.filtered(lambda hol: hol.state == 'accept').activity_unlink(['disciplinary.mail_act_employee_appeal'])

    def accept_update1(self):
        self.filtered(lambda hol: hol.state == 'accept').activity_unlink(['disciplinary.mail_act_employee_appeal'])

    def _get_responsible_for_upheld(self):
        if self.employee.parent_id:
            return self.employee.parent_id.user_id
        return self.env.user

    def upheld_update(self):
        for expense_report in self.filtered(lambda hol: hol.state == 'upheld'):
            self.activity_schedule(
                'disciplinary.mail_act_employee_appeal',
                user_id=expense_report.sudo()._get_responsible_for_upheld().id)

    def _get_responsible_for_upheld1(self):
        if self.employee:
            return self.employee.user_id
        return self.env.user

    def upheld1_update(self):
        for expense_report in self.filtered(lambda hol: hol.state == 'upheld'):
            self.activity_schedule(
                'disciplinary.mail_act_employee_appeal',
                user_id=expense_report.sudo()._get_responsible_for_upheld1().id)
        self.filtered(lambda hol: hol.state == 'upheld').activity_unlink(['disciplinary.mail_act_employee_appeal1'])

    def _get_responsible_for_refuse(self):
        if self.employee:
            return self.employee.user_id
        return self.env.user

    def refuse_update(self):
        for expense_report in self.filtered(lambda hol: hol.state == 'refuse'):
            self.activity_schedule(
                'disciplinary.mail_act_employee_appeal2',
                user_id=expense_report.sudo()._get_responsible_for_refuse().id)
        self.filtered(lambda hol: hol.state == 'refuse').activity_unlink(['disciplinary.mail_act_employee_appeal'])
        self.filtered(lambda hol: hol.state == 'refuse').activity_unlink(['disciplinary.mail_act_employee_appeal1'])
