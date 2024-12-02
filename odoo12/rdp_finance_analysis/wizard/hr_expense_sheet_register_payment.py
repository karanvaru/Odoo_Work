# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from werkzeug import url_encode

class HrExpenseSheetRegisterPaymentWizard(models.TransientModel):

    _inherit = "hr.expense.sheet.register.payment.wizard"

    finance_analysis = fields.Boolean(string='Finance Analysis', default=True, track_visibility=True)
    is_active = fields.Boolean(invisible=1, compute="compute_active", store=True)
    office_location_id = fields.Many2one('office.location', string="Office Location", track_visibility=True)
    multiple_office_location_ids = fields.Many2many('office.location', string='Multiple Office Location', track_visibility=True)
    transaction_category_id = fields.Many2one('transaction.category', string='Transaction Category',track_visibility=True)
    transaction_sub_category_id = fields.Many2one('transaction.sub.category', string='Transaction Sub Category',track_visibility=True)
    transaction_category_type_id = fields.Many2one('transaction.category.type', string='Transaction Category Type',track_visibility=True)

    @api.depends('office_location_id')
    def compute_active(self):
        for rec in self:
            if rec.office_location_id:
                if rec.office_location_id.code == 'CO':
                    rec.is_active = True

    def _get_payment_vals(self):
        """ Hook for extension """
        return {
            'partner_type': 'supplier',
            'payment_type': 'outbound',
            'partner_id': self.partner_id.id,
            'partner_bank_account_id': self.partner_bank_account_id.id,
            'journal_id': self.journal_id.id,
            'company_id': self.company_id.id,
            'payment_method_id': self.payment_method_id.id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'payment_date': self.payment_date,
            'communication': self.communication, 
            'finance_analysis': self.finance_analysis, 
        }

    @api.multi
    def expense_post_payment(self):
        self.ensure_one()
        context = dict(self._context or {})
        print('context===========',context)
        active_ids = context.get('active_ids', [])
        print('active_ids===========',active_ids)
        expense_sheet = self.env['hr.expense.sheet'].browse(active_ids)

        # Create payment and post it 
        payment = self.env['account.payment'].create(self._get_payment_vals())
        payment.post()
        analysis = self.env['finance.analysis'].search([('account_payment_id','=',payment.id)])
        analysis.update({
                        'office_location_id':self.office_location_id.id,
                        'multiple_office_location_ids':[(6,0, [mol.id for mol in self.multiple_office_location_ids])],
                        'transaction_category_id':self.transaction_category_id.id,
                        'transaction_sub_category_id':self.transaction_sub_category_id.id,
                        'transaction_category_type_id':self.transaction_category_type_id.id
                        })
        # Log the payment in the chatter
        body = (_("A payment of %s %s with the reference <a href='/mail/view?%s'>%s</a> related to your expense %s has been made.") % (payment.amount, payment.currency_id.symbol, url_encode({'model': 'account.payment', 'res_id': payment.id}), payment.name, expense_sheet.name))
        expense_sheet.message_post(body=body)

        # Reconcile the payment and the expense, i.e. lookup on the payable account move lines
        account_move_lines_to_reconcile = self.env['account.move.line']
        for line in payment.move_line_ids + expense_sheet.account_move_id.line_ids:
            if line.account_id.internal_type == 'payable':
                account_move_lines_to_reconcile |= line
        account_move_lines_to_reconcile.reconcile()

        return {'type': 'ir.actions.act_window_close'}
