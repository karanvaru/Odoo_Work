from odoo import models, api, fields, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_report_payslip_lines(self):
        earn_line = []
        deduct_line = []
        total_earn = 0
        total_ded = 0
        for line in self.line_ids.filtered(lambda i: i.salary_rule_id.code not in ['NET', 'GROSS', 'TOTAL_DED']):
            if line.total > 0:
                earning = line.name
                earning_amount = int(line.total)
                total_earn += earning_amount
                earn_line.append({
                    'earning': earning,
                    'earning_amount': earning_amount,
                })
            elif line.total < 0:
                deduction = line.name
                deduction_amount = int(abs(line.total))
                total_ded += deduction_amount
                deduct_line.append({
                    'deduction': deduction,
                    'deduction_amount': deduction_amount,
                })
        net_salary_payable = total_earn - total_ded
        return earn_line, deduct_line, total_ded, net_salary_payable

    def _compute_salary_days(self):
        for payslip in self:
            if payslip.date_to and payslip.date_from:
                start_date = payslip.date_from
                end_date = payslip.date_to
                if payslip.contract_id.date_start and payslip.contract_id.date_start > start_date:
                    start_date = payslip.contract_id.date_start
                if payslip.contract_id.date_end and payslip.contract_id.date_end < end_date:
                    end_date = payslip.contract_id.date_end

                payslip_salary_days = (end_date - start_date).days + 1
                return payslip_salary_days
            else:
                payslip_salary_days = 0
                return payslip_salary_days

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _get_emp_leaves(self):
        
        leave_types = self.env['hr.leave'].search([
            ('employee_id', '=', self.id)
        ]).mapped('holiday_status_id')
        
        leave_names = {}
        for leave_type in leave_types:
            leave_names[leave_type.id] = leave_type.name
        
        result = leave_types.get_employees_days(self.ids)
        
        leave_data = result[self.id]
        return leave_names, leave_data


