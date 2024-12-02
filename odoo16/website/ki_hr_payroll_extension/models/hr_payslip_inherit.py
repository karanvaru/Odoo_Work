from odoo import _, api, fields, models
from datetime import date
from dateutil.relativedelta import relativedelta


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    month_days = fields.Float(
        string='Month Days',
        compute='compute_month_days',
        store=True
    )
    per_day_salary = fields.Float(
        string='Per Day Salary',
        compute='compute_per_day_salary'
    )
    working_day = fields.Float(
        string='Working Days',
        compute="compute_working_day",
        store=True
    )
    state = fields.Selection(
        selection_add=[('paid', 'Paid')]
    )
    payslip_amount = fields.Float(
        compute="_compute_payslip_amount",
        string="Amount",
        store=True
    )

    @api.depends('line_ids', 'line_ids.code', 'line_ids.amount')
    def _compute_payslip_amount(self):
        for rec in self:
            net_line = rec.line_ids.filtered(lambda i: i.code == 'NET')
            rec.payslip_amount = 0
            if net_line:
                rec.payslip_amount = net_line[0].total
        

    @api.depends('date_from', 'date_to')
    def compute_month_days(self):
        for record in self:
            record.month_days=0
            if record.date_from and record.date_to:
                record.month_days = (record.date_to - record.date_from).days + 1

    @api.depends('date_from', 'date_to', 'contract_id')
    def compute_working_day(self):
        for record in self:
            record.working_day=0
            
            if record.contract_id and record.date_from and record.date_to:
                date_from = record.date_from
                date_to = record.date_to
    
                if record.contract_id.date_start > date_from:
                    date_from = record.contract_id.date_start
    
                if record.contract_id.date_end and record.contract_id.date_end < date_to:
                    date_to = record.contract_id.date_end
    
                record.working_day = (date_to - date_from).days + 1


    @api.depends('per_day_salary')
    def compute_per_day_salary(self):
        for rec in self:
            rec.per_day_salary = rec.contract_id.wage / rec.month_days
