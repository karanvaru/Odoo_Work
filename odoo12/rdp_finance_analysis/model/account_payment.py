from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    finance_analysis = fields.Boolean(string='Finance Analysis', default=False, track_visibility=True)
    finance_analysis_ids = fields.One2many('finance.analysis','account_payment_id', string="Finance Analysis", track_visibility=True)
    analysis_count = fields.Integer(compute='compute_analysis_count')
    remaining_amount = fields.Monetary(string="FA Differ Amount",track_visibility=True, compute ='compute_remaining_amount',store=True)

    @api.depends('amount','finance_analysis_ids','finance_analysis_ids.amount')
    def compute_remaining_amount(self):
        for record in self:
            payment=record['id']
            if payment:
                total_rec = self.env['finance.analysis'].search([('account_payment_id.id','=',payment)])
                record['remaining_amount']= record['amount']
                for rec in total_rec:
                    record['remaining_amount'] -= rec['amount']

    @api.multi
    def post(self):
        res = super().post()
        for rec in self:
            if rec.finance_analysis != True:
                raise UserError(_('Kindly Enable Finance Analysis for the Transaction !!!'))
        for res in rec.finance_analysis_ids :
            if rec.remaining_amount != 0:
                raise UserError(_('Invalid Transaction 1! Kindly verify the FA Differ Amount !'))
        analysis = self.env['finance.analysis'].search([('account_payment_id','=',self.id)])
        for obj in analysis:
            if not analysis and self.finance_analysis == True:
                res = analysis.create({
                    'account_payment_id': self.id,
                    'model': self._name,
                    'model_name': self._description,
                    'partner_id': self.partner_id.id,
                    'payment_amount': self.amount,
                    'status':self.state,
                    'source_date': self.payment_date,
                    'finance_analysis': self.finance_analysis,
                    'source_reference': self.name,
                    'remaining_amount': self.remaining_amount,
                })
            else:
                res = analysis.update({
                    'account_payment_id': self.id,
                    'model': self._name,
                    'model_name': self._description,
                    'partner_id': self.partner_id.id,
                    'payment_amount': self.amount,
                    'status':self.state,
                    'source_date': self.payment_date,
                    'finance_analysis': self.finance_analysis,
                    'source_reference': self.name,
                    'remaining_amount': self.remaining_amount
                })
        return res
    
    @api.multi
    def write(self, vals):
        res = super().write(vals)
        analysis = self.env['finance.analysis'].search([('account_payment_id','=',self.id)])
        if not analysis and self.finance_analysis == True:
            res = analysis.create({
                'account_payment_id': self.id,
                'model': self._name,
                'model_name': self._description,
                'partner_id': self.partner_id.id,
                'payment_amount': self.amount,
                'status':self.state,
                'source_date': self.payment_date,
                'finance_analysis': self.finance_analysis,
                'source_reference': self.name,
                'remaining_amount': self.remaining_amount
            })
        else:
            res = analysis.update({
                'account_payment_id': self.id,
                'model': self._name,
                'model_name': self._description,
                'partner_id': self.partner_id.id,
                'payment_amount': self.amount,
                'status':self.state,
                'source_date': self.payment_date,
                'finance_analysis': self.finance_analysis,
                'source_reference': self.name,
                'remaining_amount': self.remaining_amount
            })
        return res
    
    def compute_analysis_count(self):
        for rec in self:
            rec.analysis_count = self.env['finance.analysis'].search_count([('account_payment_id','=',self.id)])

    @api.multi
    def finance_analysis_count(self):
        self.ensure_one()
        return {
            'name': 'Accounting Transaction',
            'res_model': 'finance.analysis',
            'view_mode': 'tree,form',
            'target': 'current',
            'type': 'ir.actions.act_window',
            'domain': [('account_payment_id','=',self.id)],
        }
