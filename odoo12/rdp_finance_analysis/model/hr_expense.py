from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError

class HrExpense(models.Model):
    _inherit = 'hr.expense'

    finance_analysis = fields.Boolean(string='Finance Analysis',default=True, track_visibility=True)
    finance_analysis_ids = fields.One2many('finance.analysis','hr_expense_id', string="Finance Analysis", track_visibility=True)
    remaining_amount = fields.Monetary(string="FA Differ Amount",track_visibility=True, compute ='compute_expense_remaining_amount',store=True)
    partner_id = fields.Many2one('res.partner', compute = 'compute_employee_details',track_visibility=True)

    # @api.model
    # def search(self, args, offset=0, limit=None, order=None, count=False):
    #     # Add additional domain to filter expenses based on the current user
    #     if self.env.user.employee_id:
    #         args += [('employee_id', '=', self.env.user.employee_id.id)]
    #     return super(HrExpense, self).search(args, offset=offset, limit=limit, order=order, count=count)

    @api.onchange('employee_id')
    def compute_employee_details(self):
        for obj in self:
            obj.partner_id = obj.employee_id.address_home_id

    @api.multi
    def action_submit_expenses(self):
        for rec in self:
            if rec.finance_analysis != True:
                raise UserError(_('Kindly Enable Finance Analysis to Create Expense Report !!!'))
            if rec.remaining_amount != 0:
                raise UserError(_('Invalid Transaction ! Kindly verify the FA Differ Amount !'))
        if any(expense.state != 'draft' or expense.sheet_id for expense in self):
            raise UserError(_("You cannot report twice the same line!"))
        if len(self.mapped('employee_id')) != 1:
            raise UserError(_("You cannot report expenses for different employees in the same report."))
        todo = self.filtered(lambda x: x.payment_mode=='own_account') or self.filtered(lambda x: x.payment_mode=='company_account')
        return {
            'name': _('New Expense Report'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.expense.sheet',
            'target': 'current',
            'domain': [('finance_analysis_ids','=',self.finance_analysis_ids)],
            'context': {
                'default_expense_line_ids': todo.ids,
                'default_employee_id': self[0].employee_id.id,
                'default_name': todo[0].name if len(todo) == 1 else '',
                'default_hr_expense_id':self.id,
                'default_finance_analysis': self.finance_analysis,
            }
        }
    
    @api.depends('total_amount','finance_analysis_ids','finance_analysis_ids.amount')
    def compute_expense_remaining_amount(self):
        expense_paid = 0
        for record in self:
            for rec in record.finance_analysis_ids:
                expense_paid += rec.amount
                print('==============expense_paid',expense_paid)
                print('==============rec.amount',rec.amount)
                print('==============employee_id',record.employee_id)
            record.remaining_amount = record.total_amount - expense_paid

    