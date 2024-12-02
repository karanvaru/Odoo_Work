# -*- coding: utf-8 -*-
"""
# License LGPL-3.0 or later (https://opensource.org/licenses/LGPL-3.0).
#
# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, or if you have received a written
# agreement from the authors of the Software (see the COPYRIGHT section below).
#
# You may develop Odoo modules that use the Software as a library (typically
# by depending on it, importing it and using its resources), but without copying
# any source code or material from the Software. You may distribute those
# modules under the license of your choice, provided that this license is
# compatible with the terms of the Odoo Proprietary License (For example:
# LGPL, MIT, or proprietary licenses similar to this one).
#
# It is forbidden to publish, distribute, sublicense, or sell copies of the Software
# or modified copies of the Software.
#
# The above copyright notice and this permission notice must be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#
#########COPYRIGHT#####
# © 2019 Bernard K Too<bernard.too@optima.co.ke>
"""
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
import calendar


class KeSalaryAdvance(models.Model):
    """ Salary Advance request model"""
    _name = "ke.advance"
    _description = "Salary Advance Request"
    _inherit = ["mail.thread", 'mail.activity.mixin', 'portal.mixin']
    _order = "id desc"

    def _employee_get(self):
        return self.employee_id.search(
            [('user_id', '=', self.env.user.id)], limit=1).id

    def check_login_user(self):
        """ set boolean value based on login user """
        for record in self:
            record.same_user = bool(record.env.user.id == record.user_id.id)

    name = fields.Char(
        'Request details',
        required=True,
        readonly=True,
        tracking=True,
        states={
            'draft': [
                ('readonly',
                 False)]})
    dept_id = fields.Many2one(
        'hr.department',
        'Department',
        tracking=True,
        related='employee_id.department_id')
    employee_id = fields.Many2one(
        'hr.employee',
        'Employee Name',
        default=_employee_get,
        required=True,
        tracking=True,
        readonly=True,
        states={
            'draft': [
                ('readonly',
                 False)]})
    user_id = fields.Many2one(
        'res.users',
        related='employee_id.user_id',
        tracking=True)
    state = fields.Selection([('draft',
                               'Draft'),
                              ('approval',
                               'Waiting Approval'),
                              ('approved',
                               'Approved'),
                              ('disapproved',
                               'Dis-approved')],
                             'Status',
                             default='draft', tracking=True)
    amount = fields.Monetary(
        'Amount',
        currency_field='currency_id',
        tracking=True, readonly=True, states={
            'draft': [
                ('readonly',
                 False)]})
    description = fields.Html(
        'Reasons for Request',
        readonly=True,
        states={
            'draft': [
                ('readonly',
                 False)]}, tracking=True)
    contract_id = fields.Many2one(
        'hr.contract',
        'Contract',
        readonly=True,
        compute="_compute_contract_id",
        store=True,
        tracking=True)

    same_user = fields.Boolean(compute='check_login_user')
    date_end = fields.Date('End Date')

    currency_id = fields.Many2one(
        related='employee_id.company_id.currency_id',
        tracking=True)

    date_start = fields.Date('Start Date', required=True)
    no_date_end = fields.Boolean('Is Recurring', default=False)

    @api.depends('employee_id')
    def _compute_contract_id(self):
        for rec in self:
            contract = self.env['hr.contract'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('state', '=', 'open')
            ], limit=1)
            if not contract:
                raise ValidationError(_("You currently do not have a contract associated to you. \n Contact HR."))

            rec.contract_id = contract.id

    def advance_approval(self):
        """ sets the draft salary advance request to waiting approval"""
        for record in self:
            if not record.employee_id:
                raise ValidationError('Missing Employee record')
            # elif not record.employee_id.parent_id:
            #     raise ValidationError(
            #         'Your manager is not added in your HR records,\
            #                 no one to approve your salary advance request.Please consult HR')
            # # elif not record.employee_id.parent_id.user_id:
            #     raise ValidationError(
            #         'Your manager does have access to the HR system to \
            #                 approve your salary advance request. Please consult HR')
            else:
                return record.write({'state': 'approval'})

    def advance_approved(self):
        """ approves a salary advance request """
        for record in self:
            deduction_type = self.env.ref('hr_ke.ke_deduction2')
            if not deduction_type:
                raise ValidationError(
                    "No salary rule found for processing salary advance in your payroll system!")
            values = {
                'employee_id': record.employee_id.id,
                'computation': 'fixed',
                'deduction_id': deduction_type.id,
                'rule_id': deduction_type.rule_id.id,
                'fixed': record.amount,
                'date_start': record.date_start,
                'date_end': record.date_end,
                'is_permanent': record.no_date_end,
                'company_id': record.employee_id.company_id.id
            }
            if values:
                self.env['ke.deductions'].create(values)
            else:
                raise ValidationError(
                    'Missing Salary Advance details. Please consult payroll department')
            record.write({'state': 'approved'})

    
    def advance_disapproved(self):
        """ disapproves a salary advance request """
        for record in self:
            record.write({'state': 'disapproved'})

    
    def advance_reset(self):
        """ resets a salary adanve request currently waiting approval"""
        for record in self:
            record.write({'state': 'draft'})
