from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError

class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    finance_analysis = fields.Boolean(string='Finance Analysis', default=False, track_visibility=True)
    finance_analysis_ids = fields.One2many('finance.analysis',related = 'hr_expense_id.finance_analysis_ids', readonly =False, string="Finance Analysis", track_visibility=True)
    analysis_count = fields.Integer(compute='compute_analysis_count')
    remaining_amount = fields.Monetary(string="FA Differ Amount",track_visibility=True, compute ='compute_expense_sheet_remaining_amount',store=True)
    partner_id = fields.Many2one('res.partner', compute = 'compute_employee_details',track_visibility=True)
    hr_expense_id = fields.Many2one('hr.expense')

    @api.onchange('employee_id')
    def compute_employee_details(self):
        for obj in self:
            obj.partner_id = obj.employee_id.address_home_id

    @api.multi 
    def action_sheet_move_create(self):
        res = super().action_sheet_move_create()
        for rec in self:
            if rec.finance_analysis != True:
                raise UserError(_('Kindly Enable Finance Analysis for this Expenses !!!'))
        for res in rec.finance_analysis_ids :
            if rec.remaining_amount != 0:
                raise UserError(_('Invalid Transaction ! Kindly verify the FA Differ Amount !'))
        analysis = self.env['finance.analysis'].search([('hr_expense_id.id','=',self.hr_expense_id.id)])
        if analysis and self.finance_analysis == True:
            res = analysis.update({
                'hr_expense_sheet_id': self.id,
                'model': self._name,
                'model_name': self._description,
                'partner_id': self.partner_id,
                'payment_amount': self.total_amount,
                'status':self.state,
                'source_date': self.hr_expense_id.date,
                'finance_analysis': self.finance_analysis,
                'source_reference': self.name,
            })
        return res
    
    @api.multi
    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            analysis = rec.env['finance.analysis'].search([('hr_expense_id.id','=',rec.hr_expense_id.id)])
            if analysis and rec.finance_analysis == True:
                res = analysis.update({
                    'hr_expense_sheet_id': rec.id,
                    'partner_id': rec.partner_id,
                    'payment_amount': rec.total_amount,
                    'source_date': rec.hr_expense_id.date,
                    'finance_analysis': rec.finance_analysis,
                    'source_reference': rec.name,
                    'status':rec.state,
                })
        return res
    
    @api.depends('total_amount','finance_analysis_ids','finance_analysis_ids.amount')
    def compute_expense_sheet_remaining_amount(self):
        expense_paid = 0
        for record in self:
            for rec in record.finance_analysis_ids:
                expense_paid += rec.amount
            record.remaining_amount = record.total_amount - expense_paid
            