# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class installment_line(models.Model):
    _name = 'installment.line'
    _description = 'Lines of an Installment'
    _order = 'date,name'

    name = fields.Char('Name')
    employee_id = fields.Many2one('hr.employee',string='Employee')
    loan_id = fields.Many2one('employee.loan',string='Loan',required="1", ondelete='cascade')
    date = fields.Date('Date')
    is_paid = fields.Boolean('Paid')
    amount = fields.Float('Loan Amount', compute='_compute_result', store=True)
    interest = fields.Float('Interest Amount')
    ins_interest = fields.Float('Interest')
    service_charge_amount = fields.Float('Service Charge Amount')
    term = fields.Integer('Term')
    loan_term = fields.Integer('Loan Term')
    # ins_service_charge = fields.Float('Service Charge')
    installment_amt = fields.Float('Installment Amount')
    total_installment = fields.Float('Total',compute='get_total_installment')
    payslip_id = fields.Many2one('hr.payslip',string='Payslip')
    is_skip = fields.Boolean('Skip Installment')

    @api.depends('installment_amt', 'ins_interest')
    def get_total_installment(self):
        for line in self:
            line.total_installment = line.ins_interest + line.installment_amt

    @api.onchange('loan_term')
    def _onchange_term(self):
        if self.loan_term != 0:
            self.amount = self.amount / self.loan_term
        else:
            self.amount = 0.0



    def action_view_payslip(self):
        if self.payslip_id:
            return {
                'view_mode': 'form',
                'res_id': self.payslip_id.id,
                'res_model': 'hr.payslip',
                'view_type': 'form',
                'type': 'ir.actions.act_window',

            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
