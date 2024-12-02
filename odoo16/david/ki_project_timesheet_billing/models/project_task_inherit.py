# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning


class ProjectTaskInherit(models.Model):
    _inherit = 'project.task'

    def create_invoice1(self):
        data_list = []
        product_id = self.env.user.company_id.config_invoice_product_id
        if not product_id:
            raise ValidationError('Add Product Before Create Invoice.')
        for rec in self:
            if (any(not i.is_invoice for i in rec.job_invoice_line_ids) or any(
                    not i.is_invoice for i in rec.job_cost_sheet_ids) or
                    any(not i.is_invoice for i in rec.job_card_daily_report_ids)):
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
                    'category_type': 'service',
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
                for timesheet in rec.job_card_daily_report_ids:
                    data_dct = {}
                    for project in rec.project_id.project_employee_rate_ids:
                        employee_rate_id = rec.project_id.project_employee_rate_ids.filtered(lambda x: x.employee_id)
                        if timesheet.employee_id not in employee_rate_id.employee_id:
                            raise ValidationError('Add Employee Hour/Rent Before Create Invoice.')
                        if timesheet.employee_id == project.employee_id:
                            if not timesheet.is_invoice:
                                data_dct['price_unit'] = project.hourly_rate
                                data_dct['quantity'] = timesheet.unit_amount
                                data_dct['name'] = timesheet.name
                                data_dct['product_id'] = product_id.id
                                data_dct['account_id'] = \
                                    product_id.product_tmpl_id.get_product_accounts(fiscal_pos=None)[
                                        'income'].id
                                # data_dct['uom_id'] = product_id.uom_id.id
                                data_list.append((0, 0, data_dct))
                                timesheet.is_invoice = True

                if to_do_job_invoice_line_ids or inv_line_lst or data_list:
                    if data_list:
                        inv_line_lst.extend(data_list)
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

    # def create_invoice1(self):
    #     res = super(ProjectTaskInherit, self).create_invoice1()
    #     data_list = []
    #     product_id = self.env.user.company_id.config_invoice_product_id
    #     if not product_id:
    #         raise ValidationError('Add Product Before Create Invoice.')
    #     for rec in self:
    #         for timesheet in rec.job_card_daily_report_ids:
    #             data_dct = {}
    #             for project in rec.project_id.project_employee_rate_ids:
    #                 employee_rate_id = rec.project_id.project_employee_rate_ids.filtered(lambda x: x.employee_id)
    #                 if timesheet.employee_id not in employee_rate_id.employee_id:
    #                     raise ValidationError('Add Employee Hour/Rent Before Create Invoice.')
    #                 if timesheet.employee_id == project.employee_id:
    #                     if not timesheet.is_invoice:
    #                         data_dct['price_unit'] = project.hourly_rate
    #                         data_dct['quantity'] = timesheet.unit_amount
    #                         data_dct['name'] = timesheet.name
    #                         data_dct['product_id'] = product_id.id
    #                         data_dct['account_id'] = product_id.product_tmpl_id.get_product_accounts(fiscal_pos=None)[
    #                             'income'].id
    #                         # data_dct['uom_id'] = product_id.uom_id.id
    #                     data_list.append((0, 0, data_dct))
    #                     timesheet.is_invoice = True
    #     # invoice = self.env['account.move'].sudo().browse(res['id'])
    #     # invoice.update({
    #     #     'invoice_line_ids':data_list
    #     # })
    #     # print("!!!!!!!!!!!!!!!!!!!!!!!!invoice", invoice)
    #
    #     # self.job_invoice_line_ids = data_list
    #     return res
