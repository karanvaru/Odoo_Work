# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

from odoo import models, fields, api


class EmployeeEntryDocuments(models.Model):
    _name = 'employee.checklist'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee Documents"

    @api.multi
    def name_get(self):
        result = []
        for each in self:
            if each.document_type == 'entry':
                name = each.name + '_en'
            elif each.document_type == 'exit':
                name = each.name + '_ex'
            elif each.document_type == 'other':
                name = each.name + '_ot'
            result.append((each.id, name))
        return result

    name = fields.Char(string='Name', copy=False, required=1)
    document_type = fields.Selection([('entry', 'Entry Process'),
                                      ('exit', 'Exit Process'),
                                      ('other', 'Other')], string='Checklist Type', help='Type of Checklist', readonly=1, required=1)


class HrEmployeeDocumentInherit(models.Model):
    _inherit = 'hr.employee.document'

    document_name = fields.Many2one('employee.checklist', string='Document', help='Type of Document', required=True)


class EmployeeMasterInherit(models.Model):
    _inherit = 'hr.employee'

    @api.depends('exit_checklist')
    def exit_progress(self):
        for each in self:
            total_len = self.env['employee.checklist'].search_count([('document_type', '=', 'exit')])
            entry_len = len(each.exit_checklist)
            if total_len != 0:
                each.exit_progress = (entry_len * 100) / total_len

    @api.depends('entry_checklist')
    def entry_progress(self):
        for each in self:
            total_len = self.env['employee.checklist'].search_count([('document_type', '=', 'entry')])
            entry_len = len(each.entry_checklist)
            if total_len != 0:
                each.entry_progress = (entry_len*100) / total_len

    @api.depends('ojt_checklist')
    def ojt_progress(self):
        for each in self:
            total_len = self.env['employee.checklist'].search_count([('document_type', '=', 'ojt')])
            entry_len = len(each.ojt_checklist)
            if total_len != 0:
                each.ojt_progress = (entry_len * 100) / total_len

    @api.depends('probation_checklist')
    def probation_progress(self):
        for each in self:
            total_len = self.env['employee.checklist'].search_count([('document_type', '=', 'probation')])
            entry_len = len(each.probation_checklist)
            if total_len != 0:
                each.probation_progress = (entry_len * 100) / total_len

    @api.depends('employment_checklist')
    def employment_progress(self):
        for each in self:
            total_len = self.env['employee.checklist'].search_count([('document_type', '=', 'employment')])
            entry_len = len(each.employment_checklist)
            if total_len != 0:
                each.employment_progress = (entry_len * 100) / total_len

    @api.depends('pre_exit_checklist')
    def pre_exit_progress(self):
        for each in self:
            total_len = self.env['employee.checklist'].search_count([('document_type', '=', 'pre_exit')])
            entry_len = len(each.pre_exit_checklist)
            if total_len != 0:
                each.pre_exit_progress = (entry_len * 100) / total_len

    @api.depends('post_exit_checklist')
    def post_exit_progress(self):
        for each in self:
            total_len = self.env['employee.checklist'].search_count([('document_type', '=', 'post_exit')])
            entry_len = len(each.post_exit_checklist)
            if total_len != 0:
                each.post_exit_progress = (entry_len * 100) / total_len

    @api.depends('induction_checklist')
    def induction_progress(self):
        for each in self:
            total_len = self.env['employee.checklist'].search_count([('document_type', '=', 'induction')])
            entry_len = len(each.induction_checklist)
            if total_len != 0:
                each.induction_progress = (entry_len * 100) / total_len

    entry_checklist = fields.Many2many('employee.checklist', 'entry_obj', 'check_hr_rel', 'hr_check_rel',
                                       string='Entry Process',
                                       domain=[('document_type', '=', 'entry')])
    exit_checklist = fields.Many2many('employee.checklist', 'exit_obj', 'exit_hr_rel', 'hr_exit_rel',
                                      string='Exit Process',
                                      domain=[('document_type', '=', 'exit')])
    induction_checklist = fields.Many2many('employee.checklist', 'indu_obj', 'indu_hr_rel', 'hr_indu_rel',
                                      string='Induction Process',
                                      domain=[('document_type', '=', 'induction')])
    ojt_checklist = fields.Many2many('employee.checklist', 'ojt_obj', 'ojt_hr_rel', 'hr_ojt_rel',
                                      string='OJT Process',
                                      domain=[('document_type', '=', 'ojt')])
    probation_checklist = fields.Many2many('employee.checklist', 'probation_obj', 'probation_hr_rel', 'hr_probation_rel',
                                      string='Probation Process',
                                      domain=[('document_type', '=', 'probation')])
    employment_checklist = fields.Many2many('employee.checklist', 'employment_obj', 'employment_hr_rel', 'hr_employment_rel',
                                      string='Employment Process',
                                      domain=[('document_type', '=', 'employment')])
    pre_exit_checklist = fields.Many2many('employee.checklist', 'pre_exit_obj', 'pre_exit_hr_rel', 'hr_pre_exit_rel',
                                      string='Pre-Exit Process',
                                      domain=[('document_type', '=', 'pre_exit')])
    post_exit_checklist = fields.Many2many('employee.checklist', 'post_exit_obj', 'post_exit_hr_rel', 'hr_post_exit_rel',
                                      string='Post-Exit Process',
                                      domain=[('document_type', '=', 'post_exit')])
    entry_progress = fields.Float(compute=entry_progress, string='Entry Progress', store=True, default=0.0)
    exit_progress = fields.Float(compute=exit_progress, string='Exit Progress', store=True, default=0.0)
    induction_progress = fields.Float(compute=induction_progress, string='Induction Progress', store=True, default=0.0)
    ojt_progress = fields.Float(compute=ojt_progress, string='OJT Progress', store=True, default=0.0)
    probation_progress = fields.Float(compute=probation_progress, string='Probation Progress', store=True, default=0.0)
    employment_progress = fields.Float(compute=employment_progress, string='Employment Progress', store=True, default=0.0)
    pre_exit_progress = fields.Float(compute=pre_exit_progress, string='Pre-Exit Progress', store=True, default=0.0)
    post_exit_progress = fields.Float(compute=post_exit_progress, string='Post-Exit Progress', store=True, default=0.0)
    maximum_rate = fields.Integer(default=100)
    check_list_enable = fields.Boolean(invisible=True, copy=False)



class EmployeeDocumentInherit(models.Model):
    _inherit = 'hr.employee.document'

    @api.model
    def create(self, vals):
        result = super(EmployeeDocumentInherit, self).create(vals)
        if result.document_name.document_type == 'entry':
            result.employee_ref.write({'entry_checklist': [(4, result.document_name.id)]})
        if result.document_name.document_type == 'exit':
            result.employee_ref.write({'exit_checklist': [(4, result.document_name.id)]})
        return result

    @api.multi
    def unlink(self):
        for result in self:
            if result.document_name.document_type == 'entry':
                result.employee_ref.write({'entry_checklist': [(5, result.document_name.id)]})
            if result.document_name.document_type == 'exit':
                result.employee_ref.write({'exit_checklist': [(5, result.document_name.id)]})
        res = super(EmployeeDocumentInherit, self).unlink()
        return res


class EmployeeChecklistInherit(models.Model):
    _inherit = 'employee.checklist'

    entry_obj = fields.Many2many('hr.employee', 'entry_checklist', 'hr_check_rel', 'check_hr_rel',
                                 invisible=1)
    exit_obj = fields.Many2many('hr.employee', 'exit_checklist', 'hr_exit_rel', 'exit_hr_rel',
                                invisible=1)
