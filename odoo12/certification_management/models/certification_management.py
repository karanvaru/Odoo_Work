# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class CertificationManagement(models.Model):
    _name = "certification.management"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Certification Management'

    name = fields.Char('Name', default=lambda self: _('New'), store=True, track_visibility='onchange')
    state = fields.Selection([
        ('new', 'NEW'),
        ('applied', 'APPLIED'),
        ('live', 'LIVE'),
        ('expired', 'EXPIRED'),
        ('closed', 'CLOSED'),
    ], string='Status', default='new')
    cnumber = fields.Char('Certification Number', store=True, track_visibility='onchange')
    certification = fields.Many2one('certification.name', string='Certification', track_visibility='onchange')
    consultant = fields.Many2one('res.partner', 'Consultant', store=True)
    assigned_to = fields.Many2one('res.users', 'Assigned To', store=True, domain="[('is_int_user','=',True)]",track_visibility='onchange')
    valid_from = fields.Date(string='Valid From', store=True, track_visibility='onchange')
    valid_to = fields.Date(string='Valid to', store=True, track_visibility='onchange')
    r_date = fields.Date(string='Renew Reminder', store=True, track_visibility='onchange')
    description = fields.Text(string='Description', store=True, track_visibility='onchange')
    department = fields.Char(string="Department", compute="compute_department")
    certification_type = fields.Many2one('certification.type', string="Certification Type")
    latest_certificate = fields.Boolean(string="Latest Certificate")
    application_form_submitted = fields.Boolean(string="Application Form Submitted")
    all_test_reports = fields.Boolean(string="All Test Reports")
    all_other_documents_related_to_this_certificate = fields.Boolean(
        string="All Other Documents Related to this Certificate")
    user_id = fields.Char(string="User ID")
    password = fields.Char(string="Password")

    @api.model
    def create(self, vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code('certification.management.sequence'),
        })
        return super(CertificationManagement, self).create(vals)

    @api.multi
    def action_close(self):
        self.write({'state': 'closed'})
        return

    @api.multi
    def action_applied(self):
        self.write({'state': 'applied'})
        return

    @api.multi
    def action_live(self):
        self.write({'state': 'live'})
        return

    @api.multi
    def action_expired(self):
        self.write({'state': 'expired'})
        return

    @api.depends('assigned_to')
    def compute_department(self):
        for rec in self:
            assigned_employee_name = rec.assigned_to.name
            employee = self.env['hr.employee'].search([('user_id', '=', assigned_employee_name)])
            for dept in employee:
                rec.department = dept.department_id.name


class CertificationName(models.Model):
    _name = 'certification.name'
    name = fields.Char(required=True)


class CertificationTypeInCertificationManagement(models.Model):
    _name = "certification.type"
    _description = "Certification Management"

    name = fields.Char(string="Name")
