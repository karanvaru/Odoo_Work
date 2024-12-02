from odoo import models, fields, api


class ExpensesInherited(models.Model):
    _inherit = 'hr.expense'

    bank_details = fields.Text(string='Bank Details',required=True)
    budget_approval_bills_sumbissions = fields.Many2one('bills.approvals', string='Budget Approval Bills Submissions')
    hr_expenses_ids = fields.One2many('hr.expense.sheet', 'hr_expenses_sheet_id')



class ExpensesSheetInherited(models.Model):
    _inherit = 'hr.expense.sheet'


    bank_details = fields.Text(string='Bank Details', compute='compute_bank_details')
    hr_expenses_sheet_id = fields.Many2one('hr.expense')

    @api.depends('expense_line_ids')
    def compute_bank_details(self):
        for rec in self:
            rec.bank_details = rec.expense_line_ids.bank_details
