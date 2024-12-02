# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from ast import literal_eval
from odoo import http, tools, _
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    transmission = fields.Char(
        string="Transmission"
    )

    fuel_type = fields.Selection(
        selection="_fuel_type"
    )
    employee_count = fields.Integer(
        string="Employee Count",
        compute="_compute_employee_count"
    )
    initial_registration = fields.Char(
        string="Initial Registration"
    )
    serial_number = fields.Char(
        string='Serial Number'
    )
    engine_number = fields.Char(
        string='Engine Number'
    )
    id_number = fields.Char(
        string="Id Number"
    )
    hours = fields.Float(
        string="Hour(s)"
    )
    last_service_date = fields.Date(
        string="Last Service Date"
    )

    @api.depends('user_ids', 'workshop_staff_id', 'timesheet_ids', 'timesheet_ids.leader_id',
                 'timesheet_ids.workers_ids')
    def _compute_employee_count(self):
        self.employee_count = 0
        count = []
        user = 0
        for rec in self:
            user = self.env['res.users'].search_count([('id', '=', rec.user_ids.ids)])
            for staff in rec.workshop_staff_id:
                team_ids = self.env['hr.employee'].search([('id', '=', staff.team_ids.ids)])
                for team in team_ids:
                    count.append(team)

            for res in rec.timesheet_ids:
                leader_id = self.env['hr.employee'].search([('id', '=', res.leader_id.id)])
                for lead in leader_id:
                    count.append(lead)
                workers_ids = self.env['hr.employee'].search([('id', '=', res.workers_ids.ids)])
                for work in workers_ids:
                    count.append(work)

        count_set = set(count)
        count_lst = len(list(count_set))
        self.employee_count = count_lst + user

    @api.model
    def _fuel_type(self):
        selection = [
            ('diesel', 'Diesel'),
            ('gas', 'Gasoline'),
            ('electric', 'Electric')
        ]
        return selection

    def listToString(self, string):
        str1 = ", "
        return (str1.join(string))

    @api.onchange('product_id_helpdesk')
    def vehicle_details_set_value(self):
        for rec in self:
            rec.vin = rec.product_id_helpdesk.vin_number
            rec.engine_number = rec.product_id_helpdesk.engine_number
            rec.serial_number = rec.product_id_helpdesk.serial_number
            rec.model_name = rec.product_id_helpdesk.model_name
            rec.brand = rec.product_id_helpdesk.brand.name
            string_eng = []
            for res in rec.product_id_helpdesk.engine:
                string_eng.append(res.name)
            rec.engine = self.listToString(string_eng)
            string_tra = []
            for res in rec.product_id_helpdesk.transmission_ids:
                string_tra.append(res.name)
            rec.transmission = self.listToString(string_tra)

    @api.onchange('vin')
    def on_change_vin(self):
        for rec in self:
            product = self.env['product.product'].search([('vin_number', '=', rec.vin)], limit=1)
            rec.engine_number = product.engine_number
            rec.serial_number = product.serial_number
            rec.model_name = product.model_name
            rec.brand = product.brand.name
            string_eng = []
            for res in product.engine:
                string_eng.append(res.name)
            rec.engine = self.listToString(string_eng)
            string_tra = []
            for res in product.transmission_ids:
                string_tra.append(res.name)
            rec.transmission = self.listToString(string_tra)

    @api.onchange('serial_number')
    def on_change_serial_number(self):
        for rec in self:
            product = self.env['product.product'].search([('serial_number', '=', rec.serial_number)], limit=1)
            rec.engine_number = product.engine_number
            rec.vin = product.vin_number
            rec.model_name = product.model_name
            rec.brand = product.brand.name
            string_eng = []
            for res in product.engine:
                string_eng.append(res.name)
            rec.engine = self.listToString(string_eng)
            string_tra = []
            for res in product.transmission_ids:
                string_tra.append(res.name)
            rec.transmission = self.listToString(string_tra)

    @api.model
    def create(self, vals):
        result = super(ProjectTask, self).create(vals)
        custom_task_sequence_ignore = literal_eval(
            self.env['ir.config_parameter'].sudo().get_param('job_card.custom_task_sequence_ignore', 'False'))
        for record in result:
            if custom_task_sequence_ignore:
                if record.is_jobcard:
                    if record.partner_id and record.partner_id.country_id and record.partner_id.country_id != record.company_id.country_id:
                        seq_number = self.env['ir.sequence'].next_by_code('job.card.overseas.seq') or _('New')
                        record.number = seq_number + ': ' + vals.get('name', False)  # +' - '+partner_name
                        record.job_number = seq_number
                    else:
                        # record.number = self.env['ir.sequence'].next_by_code('project.task') +': '+vals.get('name', False)#+' - '+partner_name
                        seq_number = self.env['ir.sequence'].next_by_code('project.task.seq') or _('New')
    
                        record.number = seq_number + ': ' + vals.get('name', False)  # +' - '+partner_name
                        record.job_number = seq_number
            else:
                seq_number = self.env['ir.sequence'].next_by_code('project.task.seq') or _('New')
                # record.number = self.env['ir.sequence'].next_by_code('project.task') +': '+vals.get('name', False)#+' - '+partner_name
                record.number = seq_number + ': ' + vals.get('name', False)  # +' - '+partner_name
                record.job_number = seq_number
        return result

    def create_invoice1(self):
        for rec in self:
            if any(not i.is_invoice for i in rec.job_invoice_line_ids) or any(
                    not i.is_invoice for i in rec.job_cost_sheet_ids):
                account_invoice_obj = self.env['account.move']
                p = rec.partner_id
                rec_account = p.property_account_receivable_id
                invoice_line_obj = self.env['account.move.line']
                invoice_vale = {
                    'partner_id': rec.partner_id.id,
                    'currency_id': self.env.user.company_id.currency_id.id,
                    'journal_id': rec.journal_id.id,
                    'task_id': rec.id,
                    'move_type': 'out_invoice',
                }
                inv_line_lst = []
                to_do_job_invoice_line_ids = self.env['job.invoice.line']
                if rec.job_invoice_line_ids:
                    for line in rec.job_invoice_line_ids:
                        if not line.is_invoice:
                            invoice_line_vale = {
                                'product_id': line.product_id.id,
                                'name': line.name,
                                'account_id': line.account_id.id,
                                'analytic_distribution': {line.account_analytic_id.id: 100},
                                'quantity': line.quantity,
                                'product_uom_id': line.uom_id.id,
                                'tax_ids': [(6, 0, line.invoice_line_tax_ids.ids)],
                                'price_unit': line.price_unit,
                            }
                            if 'item_code' in invoice_line_obj._fields:
                                invoice_line_vale.update({
                                    'item_code': line.product_id.default_code
                                })
                            inv_line_lst.append((0, 0, invoice_line_vale))
                            to_do_job_invoice_line_ids += line
                if rec.job_cost_sheet_ids:
                    for cost_line in rec.job_cost_sheet_ids:
                        if not cost_line.is_invoice:
                            cost_sheet_dict = {
                                'product_id': cost_line.product_id.id,
                                'name': cost_line.name,
                                'account_id': cost_line.account_id.id,
                                'analytic_distribution': {cost_line.account_analytic_id.id: 100},
                                'quantity': cost_line.quantity,
                                'product_uom_id': cost_line.uom_id.id,
                                'tax_ids': [(6, 0, cost_line.invoice_line_tax_ids.ids)],
                                'price_unit': cost_line.price_unit,
                            }
                            if 'item_code' in invoice_line_obj._fields:
                                cost_sheet_dict.update({
                                    'item_code': line.product_id.default_code
                                })
                            inv_line_lst.append((0, 0, cost_sheet_dict))
                            # to_do_job_invoice_line_ids += cost_line
                            cost_line.write({
                                'is_invoice': True
                            })
                if to_do_job_invoice_line_ids or inv_line_lst:
                    invoice_vale.update({
                        'invoice_line_ids': inv_line_lst
                    })
                    invoice_id = account_invoice_obj.create(invoice_vale)
                    to_do_job_invoice_line_ids.write({
                        'invoice_id': invoice_id.id
                    })
                    res = self.env.ref('account.action_move_out_invoice_type')
                    res = res.sudo().read()[0]
                    res['domain'] = str([('id', '=', invoice_id.id)])
                    return res

    def write(self, vals):
        if 'stage_id' in vals:
            stage = self.env['project.task.type'].sudo().browse(vals['stage_id'])
            if stage.name.lower() == 'done':
                requistion_pending = self.material_requisition_ids.filtered(lambda i: i.state not in ['cancel', 'receive'])
                if requistion_pending:
                    raise ValidationError(_('You can not mark as done since some requisitions are still pending'))
        return super(ProjectTask, self).write(vals)
        


class JobCostSheet(models.Model):
    _inherit = 'job.cost.sheet'

    is_invoice = fields.Boolean(
        string='Is Invoice',
        readonly=True,
    )
